"""Catálogo de DGs e variantes; mecânicas ainda não cadastradas."""

DUNGEONS = (
    {
        "id": "imperador", "name": "Imperador Digimon", "acronym": "MDG",
        "npc": "Veemon", "location": "D-Terminal",
        "difficulties": ("Normal", "Fácil"), "type": "guide", "theme": "imperador",
        "description": "Guia de mecânicas em preparação.",
    },
    {
        "id": "base-imperador", "name": "Base do Imperador", "acronym": "CDGN / CDGE",
        "npc": "Veemon", "location": "D-Terminal",
        "difficulties": ("Normal", "Fácil"), "type": "guide", "theme": "imperador",
        "description": "Guia de mecânicas em preparação.",
    },
    {
        "id": "pesadelo", "name": "Pesadelo", "acronym": "",
        "npc": "Veemon", "location": "D-Terminal",
        "difficulties": ("Normal", "Difícil", "Fácil"), "type": "timer",
        "theme": "belial", "description": "Timer de mecânicas existente (Belial).",
    },
    {
        "id": "sdg", "name": "Destruição e Regeneração", "acronym": "SDG",
        "npc": "Bokomon", "location": "D-Terminal",
        "difficulties": ("Normal", "Fácil"), "type": "guide", "theme": "sdg",
        "description": "Guia de mecânicas em preparação.",
    },
    {
        "id": "darkweb", "name": "DarkWeb", "acronym": "DW",
        "npc": "Izzy", "location": "D-Terminal",
        "difficulties": (), "type": "guide", "theme": "darkweb",
        "description": "Guia de mecânicas em preparação.",
    },
    {
        "id": "never", "name": "Terra do Nunca", "acronym": "NEVER",
        "npc": "Izzy", "location": "D-Terminal",
        "difficulties": (), "type": "guide", "theme": "never",
        "description": "Guia de mecânicas em preparação.",
    },
)


def filter_dungeons(query="", difficulty="Todas"):
    search = query.strip().casefold()
    results = []
    for dungeon in DUNGEONS:
        fields = (dungeon["name"], dungeon["acronym"], dungeon["npc"] or "",
                  "Belial" if dungeon["id"] == "pesadelo" else "")
        if search and not any(search in field.casefold() for field in fields):
            continue
        if difficulty != "Todas" and difficulty not in dungeon["difficulties"]:
            continue
        results.append(dungeon)
    return results
