"""Scenario assumptions used by the expedition planner and telemetry."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Environment:
    label: str
    temperature_c: int
    speed: float
    risk_multiplier: float
    water_multiplier: float
    required: str | None = None


PROFILES = {
    "day": Environment("Clear day", -20, 1., 1., 1.),
    "night": Environment("Cold night", -75, .75, 1.35, 1., "heater"),
    "heat": Environment("Sun-exposed heat load", 8, .85, 1.18, 1.35, "cooler"),
    "dust": Environment("Dust haze", -35, .60, 1.80, 1., "visibility"),
}
EQUIPMENT = {"heater": ("Suit heater", 2.4, 1.6),
             "cooler": ("Cooling pack", 1.8, 2.4),
             "visibility": ("Navigation beacon", 1.1, .6)}


def outfit(request):
    profile = PROFILES[request["condition"]]
    selected = request.get("equipment")
    if selected is None:
        selected = [profile.required] if profile.required else []
    selected = list(dict.fromkeys(selected))
    active = [item for item in selected if item == profile.required]
    return {"label": profile.label, "temperature_c": profile.temperature_c,
            "required": [profile.required] if profile.required else [],
            "selected": selected, "active": active,
            "missing": [profile.required] if profile.required and profile.required not in selected else [],
            "gear_kg": sum(EQUIPMENT[item][1] for item in selected),
            "extra_suit_wh_per_min": sum(EQUIPMENT[item][2] for item in active),
            "water_multiplier": profile.water_multiplier}
