"""Temas por DG com substituições limitadas de cores e imagem opcional."""

from .tokens import COLORS

DUNGEON_THEMES = {
    "belial": {"accent": "#E1848C", "banner": "#35171B", "image": None},
    "imperador": {"accent": "#D7A86C", "banner": "#473025", "image": None},
    "pesadelo": {"accent": "#B58ACF", "banner": "#352440", "image": None},
    "sdg": {"accent": "#83B7CB", "banner": "#233A47", "image": None},
    "darkweb": {"accent": "#A489EA", "banner": "#2D2550", "image": None},
    "never": {"accent": "#95C9A4", "banner": "#263D35", "image": None},
}


def get_dungeon_theme(theme_id):
    return dict(DUNGEON_THEMES.get(theme_id, {
        "accent": COLORS["gold"],
        "banner": COLORS["surface"],
        "image": None,
    }))
