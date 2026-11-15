"""Persistent expedition planning, resource accounting, and crew snapshots."""
import json
import math
import os
import sqlite3
import uuid
from pathlib import Path

from app.environment import EQUIPMENT, outfit
from app.survey_atlas import summarize

STOCK = {"oxygen_l": 120000, "water_l": 800, "suit_wh": 180000,
         "kit_wh": 80000, "robot_wh": 90000, "crew_minutes": 36000}
ALLOCATION = {"oxygen_l": 700, "water_l": 4, "suit_wh": 800, "kit_wh": 450}
RESERVE = .20
GOAL = 120
SOL_MINUTES = 1479.6
BASE_QUARTER = {"oxygen_l": 28, "water_l": 1.25, "habitat_wh": 540}
STOCK["habitat_wh"] = 480000


def database_path():
    return Path(os.environ.get("MARS_HABITAT_DB",
                str(Path.home() / "MarsHabitat" / "desktop.sqlite3")))


def database():
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=20)
    db.execute("""CREATE TABLE IF NOT EXISTS expeditions (
        id TEXT PRIMARY KEY, revision INTEGER NOT NULL, status TEXT NOT NULL,
        request TEXT NOT NULL, report TEXT NOT NULL, cost TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS habitat_cycles (
        number INTEGER PRIMARY KEY, cost TEXT NOT NULL)""")
    if db.execute("PRAGMA user_version").fetchone()[0] < 1:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("PRAGMA user_version").fetchone()[0] < 1:
            for expedition_id, raw in db.execute("""SELECT id,report FROM expeditions
                    WHERE status='complete' AND json_extract(report,'$.atlas_sectors') IS NULL""").fetchall():
                previous = json.loads(raw)
                if previous.get("hazard"):
                    previous["atlas_sectors"] = summarize(previous)
                    db.execute("UPDATE expeditions SET report=? WHERE id=?", (json.dumps(previous),expedition_id))
            db.execute("PRAGMA user_version=1")
        db.commit()
    return db


def snapshot(db):
    stock = STOCK.copy()
    history = []
    sectors = {}
    rows = db.execute("""SELECT id, request, cost,
                                json_extract(report,'$.after.path'),
                                json_extract(report,'$.rover_path'),
                                json_extract(report,'$.atlas_sectors') FROM expeditions
                         WHERE status='complete' ORDER BY revision""")
    for expedition_id, request, raw_cost, eva, rover, atlas in rows:
        costs = json.loads(raw_cost)
        for key, amount in costs.items():
            stock[key] -= amount
        settings = json.loads(request)
        if atlas:
            for key, section in json.loads(atlas).items():
                previous = sectors.get(key)
                # Removing a known exclusion requires broad coverage and a ground visit.
                if (previous and previous["status"]=="hazard" and section["status"]!="hazard"
                        and not (section["status"]=="completed" and section["coverage_pct"]>=85)):
                    continue
                sectors[key] = {**section, "expedition":len(history)+1, "condition":settings["condition"]}
        history.append({"id": expedition_id, "center": settings["center"],
                        "objective": settings["objective"], "condition": settings["condition"],
                        "completed_eva": costs["crew_minutes"] > 0,
                        "eva": json.loads(eva or "[]"), "rover": json.loads(rover or "[]"), "checks": []})
    cycles = db.execute("SELECT cost FROM habitat_cycles").fetchall()
    for (raw_cost,) in cycles:
        for key, amount in json.loads(raw_cost).items():
            stock[key] -= amount
    completed = sum(row["completed_eva"] for row in history)
    draft = db.execute("SELECT id FROM expeditions WHERE status='draft'").fetchone()
    return {"active_draft":draft[0] if draft else None, "goal": GOAL, "completed": completed, "revision": len(history) + len(cycles), "expeditions":len(history),
            "sol_elapsed":len(cycles)/4 + db.execute("SELECT COALESCE(SUM(json_extract(report,'$.habitat.duration_minutes')),0) FROM expeditions WHERE status='complete'").fetchone()[0]/SOL_MINUTES,
            "remaining": {key: round(value, 3) for key, value in stock.items()},
            "initial": STOCK, "reserve": RESERVE, "history": history, "atlas_sectors": list(sectors.values())}


def status():
    with database() as db:
        return snapshot(db)


def crew_use(minutes, load, gear=None):
    gear = gear or {"water_multiplier":1,"extra_suit_wh_per_min":0}
    return {"crew_minutes": minutes, "oxygen_l": 2 * 1.65 * minutes * (1 + load / 65),
            "water_l": 2 * .009 * minutes * (1 + load / 65) * gear["water_multiplier"],
            "suit_wh": (2 * 1.9 + gear["extra_suit_wh_per_min"]) * minutes, "kit_wh": .9 * minutes + 4}


def measure(report, request, terrain, stock):
    costs = dict.fromkeys(STOCK, 0.0)
    reasons = []
    audit = report["decision_audit"]
    gear = outfit(request) if "condition" in request else None
    for sortie in audit["sorties"]:
        used = crew_use(sortie["walking_minutes"] + sortie["science_minutes"], request["payload_kg"] + (gear["gear_kg"] if gear else 0), gear)
        limits = {**ALLOCATION, "crew_minutes": request["budget"]}
        sortie["resource_use"] = {key: round(value, 3) for key, value in used.items()}
        for key, value in used.items():
            costs[key] += value
            usable = limits[key] * (1 - RESERVE)
            if value > usable + .01:
                reasons.append(f'Sortie {sortie["sortie"]}: {key} needs {value:.2f}, usable after reserve {usable:.2f}.')
    def length(path):
        return sum(math.hypot((a[0]-b[0])*terrain["dy_m"], (a[1]-b[1])*terrain["dx_m"])
                   for a,b in zip(path,path[1:]))
    robot_legs = {}
    for key in ("uav_path", "uav_follow_up_path", "rover_path"):
        path = report.get(key, [])
        if len(path) > 1:
            robot_legs[key] = 4 + length(path)*(.009 if key == "rover_path" else .014)
    if audit["sorties"]:
        robot_legs["uav_escort"] = 4 + length(report["after"]["path"])*.014
    costs["robot_wh"] = sum(robot_legs.values())
    audit["robot_leg_wh"] = robot_legs
    for key, amount in costs.items():
        usable = max(0, stock[key] - STOCK[key] * RESERVE)
        if amount > usable + .00001:
            reasons.append(f'Habitat {key}: needs {amount:.2f}, usable after reserve {usable:.2f}.')
    return {key: round(value, 3) for key,value in costs.items()}, reasons


def prepare(request, build, terrain):
    with database() as db:
        state = snapshot(db)
        existing = db.execute("SELECT id,report FROM expeditions WHERE status='draft'").fetchone()
    if existing and json.loads(existing[1])["habitat"].get("started") and not request.get("new_expedition"):
        raise ValueError("An unfinished expedition exists. Choose Resume or Run expedition.")
    if state["completed"] >= GOAL:
        raise ValueError("Campaign objective achieved")
    # Derive a fresh reproducible observation seed from the campaign position.
    request = {**request, "seed": (request["seed"] + state["revision"]) % 2147483648}
    gear = outfit(request)
    def ceiling(key, limit):
        load = request["payload_kg"] + gear["gear_kg"]
        rates = {"oxygen_l":3.3*(1+load/65), "water_l":.018*(1+load/65)*gear["water_multiplier"],
                 "suit_wh":3.8+gear["extra_suit_wh_per_min"], "kit_wh":.9}
        return (limit - (4 if key == "kit_wh" else 0)) / rates[key]
    caps = {key: ceiling(key, min(limit * .8, state["remaining"][key] - STOCK[key] * RESERVE)) / .8
            for key, limit in ALLOCATION.items()}
    caps["crew_minutes"] = (state["remaining"]["crew_minutes"] - STOCK["crew_minutes"] * RESERVE) / .8
    limiting = min(caps, key=caps.get)
    effective = min(request["budget"], caps[limiting])
    config = {**request, "budget": max(1, effective), "payload_kg":request["payload_kg"]+gear["gear_kg"]}
    if effective < 1:
        config["eva_goals"] = 0
    report = build(config)
    if not report.get("uav_path"):
        return report
    costs, reasons = measure(report, request, terrain, state["remaining"])
    if request["eva_goals"] and gear["missing"]:
        reasons.extend(f'{EQUIPMENT[item][0]} required for {gear["label"]}.' for item in gear["missing"])
    if not any(costs.values()):
        reasons.append("No modeled activity to record")
    expedition_id = uuid.uuid4().hex
    ground_scale = .85 if report.get("uav_follow_up_path") else 1.
    phase_bounds = {"survey": [0, .35*ground_scale],
                    "rover": [.35*ground_scale, (.65 if report.get("ground_verify") else 1)*ground_scale],
                    "eva": [(.65 if report.get("ground_verify") else .35)*ground_scale, ground_scale],
                    "follow_up": [.85, 1]}
    minutes = costs["crew_minutes"] + costs["robot_wh"] / 5
    report["habitat"] = {"duration_minutes": minutes, "phase_bounds":phase_bounds,
                         "robot_legs":report["decision_audit"]["robot_leg_wh"],
                         "progress": 0., "gear":gear, "started":False, "sol_start": state["sol_elapsed"],"id": expedition_id, "cost": costs, "rejections": reasons,
                         "inventory_before": state["remaining"], "expedition": state["expeditions"] + 1,
                         "effective_budget": round(config["budget"], 2),
                         "budget_reason": (f"Crew planning constrained by {limiting}" if effective < request["budget"]
                                           else "Crew time budget is the active per-sortie limit")}
    report["request"] = request
    report["atlas_sectors"] = summarize(report)
    shortest = min((route for route in report["decision_audit"]["route_candidates"]
                    if not route["selected"]), key=lambda route:route["ranking_score"], default=None)
    selected = next((route for route in report["decision_audit"]["route_candidates"] if route["selected"]), None)
    if reasons:
        advice = {"action":"Hold expedition", "detail":reasons[0],
                  "next_step":"Reduce the survey radius or payload, or defer until resources permit."}
    elif not report["decision_audit"]["sorties"]:
        advice = {"action":"Robot-only plan", "detail":"No crew round trip passed the terrain and return checks.",
                  "next_step":"Review excluded cells and try a reachable science area closer to base."}
    elif report.get("outstanding_eva"):
        advice = {"action":"Record feasible sorties only", "detail":f'{report["outstanding_eva"]} EVA stops remain pending.',
                  "next_step":"Check the outstanding stops and plan a separate sortie if the resource reserve permits."}
    else:
        advice = {"action":"Review and record after playback",
                  "detail":f'{report["sortie_count"]} EVA sorties passed the configured resource checks.',
                  "next_step":"Check the return event and the final projected stock before recording."}
    if selected and shortest:
        advice["comparison"] = (f'Selected route score {selected["ranking_score"]:.5f}; '
                                f'next candidate {shortest["ranking_score"]:.5f}. Lower is preferred after visit count.')
    report["habitat"]["advice"] = advice
    if not reasons:
        with database() as db:
            db.execute("BEGIN IMMEDIATE")
            if snapshot(db)["revision"] != state["revision"]:
                raise ValueError("Inventory changed while planning. Generate a new plan.")
            current = db.execute("SELECT id,report FROM expeditions WHERE status='draft'").fetchone()
            if (current and (not existing or existing[0] != current[0])) or (
                current and not request.get("new_expedition") and json.loads(current[1])["habitat"].get("started")
            ):
                raise ValueError("The active expedition changed during analysis.")
            db.execute("UPDATE expeditions SET status='superseded' WHERE status='draft'")
            db.execute("INSERT INTO expeditions VALUES (?,?,?,?,?,?)",
                       (expedition_id,state["revision"],"draft",json.dumps(request),json.dumps(report),json.dumps(costs)))
    return report


def commit(expedition_id):
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT revision,status,report FROM expeditions WHERE id=?", (expedition_id,)).fetchone()
        if row is None:
            raise ValueError("Plan expired. Generate a new expedition.")
        if row[1] == "complete":
            return snapshot(db)
        if row[1] != "draft":
            raise ValueError("This expedition was superseded.")
        plan = json.loads(row[2])["habitat"]
        if not plan.get("started") or plan.get("progress",0) < 1:
            raise ValueError("Start and finish expedition playback before recording.")
        if row[0] != snapshot(db)["revision"]:
            raise ValueError("Inventory changed. Generate a new plan.")
        db.execute("UPDATE expeditions SET status='complete' WHERE id=?", (expedition_id,))
        return snapshot(db)


def start_expedition(expedition_id):
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT revision,report FROM expeditions WHERE id=? AND status='draft'",
                         (expedition_id,)).fetchone()
        if not row or row[0] != snapshot(db)["revision"]:
            raise ValueError("Preflight is stale. Analyze the mesh again.")
        report = json.loads(row[1])
        report["habitat"]["started"] = True
        db.execute("UPDATE expeditions SET report=? WHERE id=?", (json.dumps(report),expedition_id))
        return report["habitat"]


def load_draft():
    with database() as db:
        row = db.execute("SELECT report FROM expeditions WHERE status='draft'").fetchone()
    if not row:
        raise ValueError("No unrecorded expedition")
    return json.loads(row[0])


def replay(expedition_id):
    with database() as db:
        row = db.execute("SELECT report FROM expeditions WHERE id=? AND status='complete'", (expedition_id,)).fetchone()
        if not row:
            raise ValueError("Expedition not found")
        result = json.loads(row[0])
        result["habitat"]["recorded"] = True
        return result


def advance_habitat(expected_revision):
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        state = snapshot(db)
        if expected_revision != state["revision"]:
            raise ValueError("Campaign changed. Refresh before advancing the habitat clock.")
        if db.execute("SELECT 1 FROM expeditions WHERE status='draft'").fetchone():
            raise ValueError("Record or discard the current expedition before advancing habitat time.")
        for key, amount in BASE_QUARTER.items():
            if state["remaining"][key] - amount < STOCK[key]*RESERVE:
                raise ValueError(f"Habitat hold: advancing would breach the {key} reserve.")
        db.execute("INSERT INTO habitat_cycles(cost) VALUES (?)", (json.dumps(BASE_QUARTER),))
        return snapshot(db)


def discard(expedition_id):
    with database() as db:
        db.execute("DELETE FROM expeditions WHERE id=? AND status='draft'", (expedition_id,))
        return snapshot(db)


def telemetry(report, progress):
    plan = report["habitat"]
    bounds = plan["phase_bounds"]
    def fraction(phase):
        begin, end = bounds[phase]
        return min(1., max(0., (progress-begin)/(end-begin)))
    def point(path, at):
        if not path:
            return report["base"]
        index = at * (len(path)-1)
        i = int(index)
        return [a+(b-a)*(index-i) for a,b in zip(path[i],path[min(i+1,len(path)-1)])]
    def path_distance(path, at):
        if len(path) < 2:
            return 0.
        index = at*(len(path)-1)
        return sum(math.hypot(b[0]-a[0],b[1]-a[1])*min(1.,max(0.,index-i))
                   for i,(a,b) in enumerate(zip(path,path[1:])))
    path = report.get("after",{}).get("path",[])
    edge_index = fraction("eva") * max(0,len(path)-1)
    spent = dict.fromkeys(STOCK, 0.)
    active = None
    carry = ALLOCATION.copy()
    for sortie in report["decision_audit"]["sorties"]:
        samples = sortie["elapsed_minutes"]
        index = edge_index-sortie["route_index"]
        if index <= 0:
            continue
        k = min(len(samples)-1,int(index))
        if k == len(samples)-1:
            share = 1.
        else:
            active = sortie["sortie"]
            share = (samples[k]+(samples[k+1]-samples[k])*(index-k))/max(.001,samples[-1])
        for key, value in sortie["resource_use"].items():
            spent[key] += value*share
            if k < len(samples)-1 and key in carry:
                carry[key] -= value*share
    for phase, key in (("survey","uav_path"),("rover","rover_path"),("follow_up","uav_follow_up_path"),("eva","uav_escort")):
        route = path if key == "uav_escort" else report.get(key,[])
        at = fraction(phase)
        total = path_distance(route,1.)
        share = path_distance(route,at)/total if total else at
        spent["robot_wh"] += plan["robot_legs"].get(key,0.)*share
    if progress >= 1:
        spent = plan["cost"].copy()
    warnings = []
    if active:
        warnings = [key for key,value in carry.items() if value <= ALLOCATION[key]*.25]
    return {"progress":progress, "active_sortie":active,
            "state_label": ("Crew on EVA" if active else "Crew at habitat"),
            "uav_grid":point(report.get("uav_follow_up_path",[]),fraction("follow_up")) if progress>=.85 and report.get("uav_follow_up_path") else
             point(path,fraction("eva")) if active else point(report.get("uav_path",[]),fraction("survey")), "sol_elapsed":plan["sol_start"] + plan["duration_minutes"]*progress/SOL_MINUTES,
            "crew_grid":point(path,fraction("eva")), "rover_grid":point(report.get("rover_path",[]),fraction("rover")),
            "spent":{key:round(value,3) for key,value in spent.items()},
            "remaining":{key:round(plan["inventory_before"][key]-value,3) for key,value in spent.items()},
            "equipment_active":plan.get("gear",{}).get("active",[]) if active else [],
            "ambient_temperature_c":plan.get("gear",{}).get("temperature_c"),
            "crew_pack":{key:round(value,3) for key,value in carry.items()} if active else None,
            "near_reserve":warnings}


def publish_progress(expedition_id, progress, sequence):
    with database() as db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute("SELECT report,status FROM expeditions WHERE id=?", (expedition_id,)).fetchone()
        if not row or row[1] == "superseded":
            raise ValueError("Expedition is no longer current")
        report = json.loads(row[0])
        if row[1] == "draft" and progress > 0 and not report["habitat"].get("started"):
            raise ValueError("Start the expedition before publishing playback.")
        reading = telemetry(report, progress)
        db.execute("""UPDATE expeditions SET report=json_set(report,'$.habitat.progress',?,'$.habitat.sequence',?)
                   WHERE id=? AND status='draft' AND COALESCE(json_extract(report,'$.habitat.sequence'),0)<?""",
                   (progress, sequence, expedition_id, sequence))
        return reading


def crew_status():
    with database() as db:
        state = snapshot(db)
        row = db.execute("SELECT status,report FROM expeditions ORDER BY revision DESC, status DESC LIMIT 1").fetchone()
    latest = None
    if row:
        source = json.loads(row[1])
        phase = source["habitat"].get("phase_bounds")
        if phase:
            progress = 1. if row[0] == "complete" else source["habitat"]["progress"]
            latest = telemetry(source,progress)
            latest["uav_readings"] = [sample for sample in source.get("uav_readings", [])
                                      if sample["progress"]*phase["survey"][1]/.35 <= progress]
            start,end = phase["rover"]
            latest["ground_checks"] = [sample for sample in source.get("ground_checks", [])
                                       if start + sample["fraction"]*(end-start) <= progress]
            latest["state"] = "SIMULATED " + row[0].upper()
            latest["expedition"] = source["habitat"]["expedition"]
            latest["condition"] = source["request"]["condition"]
            latest["survey_center"] = source["request"]["center"]
            latest["events"] = [event for event in source.get("events",[]) if event["t"] <= progress][-6:]
        else:
            latest = {"state":"ARCHIVED V3 EXPEDITION","request":source.get("request")}
    state.pop("history")
    state.pop("atlas_sectors")
    return {**state, "latest": latest}
