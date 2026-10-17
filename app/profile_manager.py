import copy
import re

from .events import REAL_EVENTS


def create_default_profile():

    mechanics = []

    for event in REAL_EVENTS:
        mechanics.append({
            "id": event["id"],
            "name": event["name"],
            "start_time": event["time"]
        })

    return {"mechanics": mechanics}


DEFAULT_PROFILE = create_default_profile()


def clone_default_profile():

    return copy.deepcopy(DEFAULT_PROFILE)


def format_mmss(seconds):

    if seconds is None:
        return ""

    minutes, remainder = divmod(int(seconds), 60)
    return "{:02d}:{:02d}".format(minutes, remainder)


def parse_mmss(value):

    normalized = value.strip()

    match = re.fullmatch(r"(\d{1,3}):([0-5]\d)", normalized)

    if match is None:
        raise ValueError("Use o formato MM:SS.")

    minutes = int(match.group(1))
    seconds = int(match.group(2))
    return minutes * 60 + seconds


def validate_profile(profile):

    if not isinstance(profile, dict):
        return None, "O perfil precisa ser um objeto."

    mechanics = profile.get("mechanics")
    if not isinstance(mechanics, list) or len(mechanics) != len(REAL_EVENTS):
        return None, "O perfil deve manter todas as mecânicas da sequência."

    normalized_mechanics = []
    previous_start = -1

    for index, (item, template) in enumerate(zip(mechanics, REAL_EVENTS)):
        if not isinstance(item, dict) or item.get("id") != template["id"]:
            return None, "A ordem fixa das mecânicas não pode ser alterada."

        name = item.get("name")
        start_time = item.get("start_time")

        if not isinstance(name, str) or not name.strip():
            return None, "Toda mecânica precisa ter um nome."

        if type(start_time) is not int or start_time < 0:
            return None, "Os horários das mecânicas devem ser segundos válidos."

        if (
            index == 0
            and start_time == 0
            and "duration_seconds" in item
        ):
            start_time = template["time"]

        if start_time < previous_start:
            return None, "Os horários devem respeitar a ordem fixa das mecânicas."

        normalized_mechanics.append({
            "id": template["id"],
            "name": name.strip(),
            "start_time": start_time
        })
        previous_start = start_time

    return {"mechanics": normalized_mechanics}, None


def build_mechanics(profile):

    normalized, error = validate_profile(profile)

    if error:
        raise ValueError(error)

    events_by_id = {
        event["id"]: event
        for event in REAL_EVENTS
    }
    scheduled_events = []

    for item in normalized["mechanics"]:
        template = events_by_id[item["id"]]
        scheduled_events.append({
            **template,
            "name": item["name"],
            "short": (
                item["name"]
                if item["name"] != template["name"]
                else template["short"]
            ),
            "time": item["start_time"]
        })

    return scheduled_events
