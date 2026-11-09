"""Regression tests for the JSON-backed menu service (stdlib only)."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from service import data


class MenuServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "menus.json"
        self.original_menus = data.menus
        self.menus_patch = patch.object(data, "menus", [])
        self.menus_patch.start()
        self.path_patch = patch.object(data, "JSON_PATH", self.store_path)
        self.path_patch.start()
        data.menus.extend(
            [
                {
                    "id": 1,
                    "name": "비빔밥",
                    "calories": 550,
                    "description": "나물과 밥",
                    "recommendation": 2,
                },
                {
                    "id": 3,
                    "name": "Ramen",
                    "calories": 600,
                    "description": "Spicy noodle soup",
                    "recommendation": 0,
                },
            ]
        )

    def tearDown(self) -> None:
        self.path_patch.stop()
        self.menus_patch.stop()
        data.menus = self.original_menus
        self.temp_dir.cleanup()

    def test_search_is_case_insensitive_and_returns_copies(self) -> None:
        result = data.search_word("RAMEN")
        self.assertEqual([menu["id"] for menu in result], [3])
        result[0]["name"] = "changed"
        self.assertEqual(data.get_one(3)["name"], "Ramen")

    def test_add_assigns_next_id_and_persists(self) -> None:
        created = data.add_menu(
            {"name": "김밥", "calories": 400, "description": "밥과 재료를 말아 만든 음식"}
        )
        self.assertEqual(created["id"], 4)
        self.assertEqual(created["recommendation"], 0)
        self.assertEqual(json.loads(self.store_path.read_text(encoding="utf-8"))[-1], created)

    def test_update_preserves_recommendation_count(self) -> None:
        updated = data.update_one(
            {"id": 1, "name": "돌솥비빔밥", "calories": 650, "description": "뜨거운 돌솥 음식"}
        )
        self.assertEqual(updated["recommendation"], 2)
        self.assertEqual(data.get_one(1)["name"], "돌솥비빔밥")

    def test_delete_and_recommend_missing_ids_return_none(self) -> None:
        self.assertIsNone(data.delete_menu(999))
        self.assertIsNone(data.update_recommend(999))
        self.assertEqual(data.delete_menu(1), 1)
        self.assertIsNone(data.get_one(1))

    def test_failed_persistence_rolls_back_mutation(self) -> None:
        with patch.object(data, "save_menus", side_effect=data.StorageError("disk full")):
            with self.assertRaises(data.StorageError):
                data.update_recommend(1)
        self.assertEqual(data.get_one(1)["recommendation"], 2)


if __name__ == "__main__":
    unittest.main()
