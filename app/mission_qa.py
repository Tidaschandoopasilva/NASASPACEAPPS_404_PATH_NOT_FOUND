"""Offline mission Q&A using a fitted intent classifier and deterministic facts."""
from functools import lru_cache
from pathlib import Path

import joblib

from app.environment import EQUIPMENT, PROFILES, outfit


@lru_cache(maxsize=1)
def classifier():
    return joblib.load(Path(__file__).resolve().parents[1] / "models/mission_qa/intent.joblib")


RESOURCES = {
    "oxygen": ("oxygen_l", "Oxygen", "L equivalent"),
    "water": ("water_l", "Water", "L"),
    "suit_power": ("suit_wh", "Suit battery", "Wh"),
    "kit_power": ("kit_wh", "Science kit battery", "Wh"),
    "robot_power": ("robot_wh", "Combined UAV and rover power", "Wh"),
}


def answer(question, settings, report=None, rejections=()):
    model = classifier()
    probs = model.predict_proba([question])[0]
    best = probs.argmax()
    gear = outfit(settings)
    plan = report["habitat"] if report else {}
    if probs[best] < .23:
        return {"topic":"unsupported", "advice":"Try a question about equipment, weather, oxygen, batteries, route choices, or expedition holds."}
    topic = str(model.classes_[best])
    if topic in RESOURCES:
        key, name, unit = RESOURCES[topic]
        if key in plan.get("cost", {}):
            cost = plan["cost"][key]
            stock = plan["inventory_before"][key]
            detail = f"{name}: {cost:.1f} {unit} projected for this expedition. Habitat stock would move from {stock:,.1f} to {stock-cost:,.1f} {unit} when recorded."
        else:
            detail = f"Analyze a feasible draft to see projected {name.lower()} use."
    elif topic in EQUIPMENT:
        label, mass, rate = EQUIPMENT[topic]
        context = next(profile.label for profile in PROFILES.values() if profile.required == topic)
        state = "active during EVA" if topic in gear["active"] else "required but missing" if topic in gear["missing"] else "inactive in this scenario"
        detail = f"{label} is required for {context}. It is {state} here. It adds {mass:g} kg when packed and draws {rate:g} Wh/min for the pair while active."
    elif topic == "equipment":
        detail = ("Required: " + ", ".join(EQUIPMENT[key][0] for key in gear["required"]) if gear["required"] else "This scenario calls for the standard EVA loadout.") + (
            ". Missing: " + ", ".join(EQUIPMENT[key][0] for key in gear["missing"]) if gear["missing"] else "")
    elif topic == "weather":
        detail = f"{gear['label']}: {gear['temperature_c']} °C simulated ambient. The scenario scales walking speed, modeled risk and applicable equipment use."
    elif topic == "holds":
        detail = " ".join(rejections) if rejections else "The current preflight reports no holds. Review the route and estimates before starting."
    elif topic == "route":
        detail = plan.get("advice", {}).get("comparison") or (
            "The planner screens for terrain reachability and round-trip limits, then prefers more visits and lower combined tail-risk and distance scores. Open Why routes were passed over for the specific exclusions.")
    elif topic == "reserve":
        detail = "The simulator protects 20% of each sortie's time and crew allocations and 20% of initial habitat stocks."
    elif topic == "sorties":
        detail = f"The draft includes {report['sortie_count']} crew sorties." if report else "Analyze a feasible draft to count the crew sorties."
    elif topic == "pending":
        detail = f"The draft has {report['outstanding_eva']} outstanding EVA targets and {report['outstanding_rover']} outstanding rover targets." if report else "Analyze a feasible draft to identify outstanding targets."
    else:
        detail = f"{plan['duration_minutes']:.1f} simulated minutes total, with a planning budget of {plan['effective_budget']:.1f} minutes per sortie before the reserve." if plan else "Analyze a feasible draft to estimate mission duration."
    return {"topic":topic, "advice":detail}
