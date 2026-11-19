import unittest

from app.dungeon_catalog import DUNGEONS, filter_dungeons
from app.design_system.theme_manager import get_dungeon_theme


class DungeonCatalogTests(unittest.TestCase):
    def test_seven_entries_including_existing_belial(self):
        self.assertEqual(len(DUNGEONS), 7)
        self.assertEqual(len({item["id"] for item in DUNGEONS}), 7)

    def test_access_information_is_correct(self):
        by_id = {item["id"]: item for item in DUNGEONS}
        for dungeon_id in ("imperador", "base-imperador", "pesadelo"):
            self.assertEqual(by_id[dungeon_id]["npc"], "Veemon")
        self.assertEqual(by_id["sdg"]["npc"], "Bokomon")
        for dungeon_id in ("darkweb", "never"):
            self.assertEqual(by_id[dungeon_id]["npc"], "Izzy")
        for dungeon_id in ("imperador", "base-imperador", "pesadelo",
                           "sdg", "darkweb", "never"):
            self.assertEqual(by_id[dungeon_id]["location"], "D-Terminal")

    def test_difficulty_filter_and_search(self):
        self.assertEqual(len(filter_dungeons(difficulty="Difícil")), 1)
        self.assertEqual(filter_dungeons(difficulty="Difícil")[0]["id"], "pesadelo")
        self.assertEqual(len(filter_dungeons("izzy")), 2)
        self.assertEqual(filter_dungeons("CDGE")[0]["id"], "base-imperador")
        self.assertEqual(filter_dungeons("  DARKWEB  ")[0]["id"], "darkweb")

    def test_unknown_difficulties_are_not_invented(self):
        for dungeon in filter_dungeons("Izzy"):
            self.assertEqual(dungeon["difficulties"], ())

    def test_themes_have_safe_fallback(self):
        self.assertTrue(get_dungeon_theme("belial")["accent"].startswith("#"))
        self.assertIsNone(get_dungeon_theme("unknown")["image"])


if __name__ == "__main__":
    unittest.main()
