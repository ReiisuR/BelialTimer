import copy
import re

from .events import REAL_EVENTS


SKILL_NAMES = {
    "guard": "GUARDA",
    "impenetrability": "IMPENETRABILIDADE",
    "protection": "PROTEÇÃO"
}


def create_default_profile():

    mechanics = []

    for index, event in enumerate(REAL_EVENTS):
        start_time = (
            0
            if index == 0
            else event["time"]
        )

        if index == 0:
            duration = event["time"] - start_time
        elif index + 1 < len(REAL_EVENTS):
            next_start = REAL_EVENTS[index + 1]["time"]
            duration = next_start - start_time
        else:
            duration = None

        mechanics.append({
            "id": event["id"],
            "name": event["name"],
            "start_time": start_time,
            "duration_seconds": duration
        })

    skills = [
        {
            "id": skill_id,
            "name": SKILL_NAMES[skill_id],
            "associations": {}
        }
        for skill_id in SKILL_NAMES
    ]

    return {
        "mechanics": mechanics,
        "skills": skills
    }


DEFAULT_PROFILE = create_default_profile()


def clone_default_profile():

    return copy.deepcopy(DEFAULT_PROFILE)


def format_mmss(seconds):

    if seconds is None:
        return ""

    minutes, remainder = divmod(int(seconds), 60)
    return "{:02d}:{:02d}".format(minutes, remainder)


def parse_mmss(value, allow_empty=False):

    normalized = value.strip()

    if not normalized and allow_empty:
        return None

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
    skills = profile.get("skills")

    if not isinstance(mechanics, list) or len(mechanics) != len(REAL_EVENTS):
        return None, "O perfil deve manter todas as mecânicas da sequência."

    if not isinstance(skills, list) or len(skills) != len(SKILL_NAMES):
        return None, "O perfil deve conter Guarda, Impenetrabilidade e Proteção."

    normalized_mechanics = []
    previous_start = -1

    for index, (item, template) in enumerate(zip(mechanics, REAL_EVENTS)):
        if not isinstance(item, dict) or item.get("id") != template["id"]:
            return None, "A ordem fixa das mecânicas não pode ser alterada."

        name = item.get("name")
        start_time = item.get("start_time")
        duration = item.get("duration_seconds")

        if not isinstance(name, str) or not name.strip():
            return None, "Toda mecânica precisa ter um nome."

        if type(start_time) is not int or start_time < 0:
            return None, "Os horários das mecânicas devem ser segundos válidos."

        if start_time < previous_start:
            return None, "Os horários devem respeitar a ordem fixa das mecânicas."

        if duration is not None and (
            type(duration) is not int or duration < 0
        ):
            return None, "As durações devem ser segundos válidos ou ficar vazias."

        normalized_mechanics.append({
            "id": template["id"],
            "name": name.strip(),
            "start_time": start_time,
            "duration_seconds": duration
        })
        previous_start = start_time

    skills_by_id = {
        skill.get("id"): skill
        for skill in skills
        if isinstance(skill, dict)
    }

    if set(skills_by_id) != set(SKILL_NAMES):
        return None, "O perfil contém skills inválidas ou duplicadas."

    event_ids = {
        event["id"]
        for event in REAL_EVENTS
    }
    normalized_skills = []

    for skill_id, skill_name in SKILL_NAMES.items():
        skill = skills_by_id[skill_id]
        associations = skill.get("associations")

        if not isinstance(associations, dict):
            return None, "As associações de skills devem ser um objeto de mecânicas."

        normalized_associations = {}

        for event_id, lead_time in associations.items():
            if event_id not in event_ids:
                return None, "Uma associação aponta para uma mecânica desconhecida."

            if lead_time is not None and (
                type(lead_time) is not int or lead_time < 0
            ):
                return None, "A antecedência deve ser um tempo válido ou ficar vazia."

            normalized_associations[event_id] = lead_time

        normalized_skills.append({
            "id": skill_id,
            "name": skill_name,
            "associations": normalized_associations
        })

    return {
        "mechanics": normalized_mechanics,
        "skills": normalized_skills
    }, None


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
            "time": item["start_time"],
            "duration_seconds": item["duration_seconds"]
        })

    return scheduled_events


def build_skill_reminders(profile, mechanics):

    normalized, error = validate_profile(profile)

    if error:
        raise ValueError(error)

    mechanics_by_id = {
        event["id"]: event
        for event in mechanics
    }
    reminders = []

    for skill in normalized["skills"]:
        for event_id, lead_time in skill["associations"].items():
            if lead_time is None:
                continue

            target = mechanics_by_id[event_id]
            reminder_time = max(
                0,
                target["time"] - lead_time
            )

            reminders.append({
                "id": "{}:{}".format(skill["id"], event_id),
                "name": skill["name"],
                "target_event_id": event_id,
                "target_time": target["time"],
                "reminder_time": reminder_time
            })

    return reminders


def due_skill_reminders(profile, mechanics, elapsed_time):

    return [
        reminder
        for reminder in build_skill_reminders(
            profile,
            mechanics
        )
        if reminder["reminder_time"] <= elapsed_time
    ]
