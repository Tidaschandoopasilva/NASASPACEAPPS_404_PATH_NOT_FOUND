"""Offline Jezero weather screening and optional public MEDA refresh."""
from datetime import date
import json
import math
from pathlib import Path
from statistics import median
from urllib.request import urlopen

from app.terrain import ROOT

MEDA = "https://mars.nasa.gov/rss/api/?feed=weather&category=mars2020&feedtype=json"


def load_meda(raw):
    records = {}
    for item in raw["sols"]:
        try:
            sol = int(item["sol"])
            stamp = date.fromisoformat(item["terrestrial_date"])
            low, high = float(item["min_temp"]), float(item["max_temp"])
            if sol < 0 or stamp > date.today() or not -180 <= low <= high <= 50:
                continue
            records[sol] = (stamp, low, high)
        except (KeyError, TypeError, ValueError):
            continue
    if not records:
        raise ValueError("The MEDA feed contains no usable temperature pairs.")
    return sorted(records.items())[-12:]


def approach(values):
    """Theil–Sen trend with a bounded one-sol extrapolation and residual spread."""
    slopes = [(b-a)/(sb-sa) for i,(sa,a) in enumerate(values) for sb,b in values[i+1:]]
    trend = max(-8., min(8., median(slopes))) if slopes else 0.
    origin = values[-1][0]
    level = median(value - trend*(sol-origin) for sol,value in values)
    spread = max(4., 1.4826*median(abs(value-level-trend*(sol-origin)) for sol,value in values))
    return round(level+trend,1),round(spread,1),round(trend,2)


def report(cache):
    path = cache / "meda-cache.json"
    raw = json.loads((path if path.exists() else ROOT/"data/meda-weather.json").read_text())
    rows = load_meda(raw)
    sol,(stamp,_,_) = rows[-1]
    age = (date.today()-stamp).days
    low, low_spread, low_trend = approach([(s,v[1]) for s,v in rows])
    high, high_spread, high_trend = approach([(s,v[2]) for s,v in rows])
    cold = low-low_spread <= -70
    heat = high+high_spread >= 0
    orbital = []
    orbital_path = cache / "orbital-context.json"
    if orbital_path.exists():
        orbital = json.loads(orbital_path.read_text())
    for entry in orbital:
        entry["age_days"] = (date.today()-date.fromisoformat(entry["date"])).days
    region_dust = any(entry["dust_flag"] and entry["age_days"] <= 3
                      and entry["instrument"] in ("MRO MARCI","MRO MCS") for entry in orbital)
    status = "historical" if age>3 else "recent archive"
    condition = "dust" if region_dust else "night" if cold else "heat" if heat else "day"
    guidance = ({"night":"Stress-test a cold EVA with the heater and review the tighter battery budget.",
                 "heat":"Stress-test a warm EVA with cooling and check hydration.",
                 "dust":"A curated orbital report flags dust. Stress-test the dust scenario with a navigation beacon.",
                 "day":"Use clear-day simulation and check the route and reserve."})[condition]
    return {"source":MEDA,"status":status,"sol":sol,"date":stamp.isoformat(),"age_days":age,
            "samples":len(rows),"low_c":low,"high_c":high,"low_spread":low_spread,
            "high_spread":high_spread,"low_trend":low_trend,"high_trend":high_trend,
            "condition":condition,"guidance":guidance,"orbital":orbital}


def refresh(cache):
    with urlopen(MEDA,timeout=8) as response:
        raw = json.loads(response.read(1_000_001))
    load_meda(raw)
    cache.mkdir(parents=True,exist_ok=True)
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w",dir=cache,delete=False,encoding="utf-8") as stream:
        json.dump(raw,stream)
        temporary=Path(stream.name)
    temporary.replace(cache/"meda-cache.json")
    return report(cache)


def import_orbital(cache, item):
    stamp=date.fromisoformat(item["date"])
    south,west,north,east=item["bounds"]
    if not all(math.isfinite(x) for x in item["bounds"]) or not (
       -90 <= south <= 18.455 <= north <= 90 and 0 <= west <= 77.440 <= east <= 360):
        raise ValueError("Product footprint must contain the Jezero reference coordinate.")
    if stamp>date.today():
        raise ValueError("Product acquisition date is in the future.")
    entry={**item,"age_days":(date.today()-stamp).days,"provenance":"operator-curated archive product"}
    cache.mkdir(parents=True,exist_ok=True)
    existing=report(cache)["orbital"]
    entries=[row for row in existing if (row["instrument"],row["product"]) != (entry["instrument"],entry["product"])]
    (cache/"orbital-context.json").write_text(json.dumps([entry,*entries][:20]))
    return report(cache)


if __name__ == "__main__":
    import argparse
    from app.main import OrbitalContext, weather_cache
    parser = argparse.ArgumentParser(description="Import a curated Jezero orbital observation")
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    item = OrbitalContext.model_validate_json(args.file.read_text(encoding="utf-8"))
    print(json.dumps(import_orbital(weather_cache(), item.model_dump()), indent=2))
