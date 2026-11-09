"""JSON-backed storage and menu operations."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


JSON_PATH = Path(__file__).resolve().parent.parent / "storage" / "menus_recommendation.json"


def load_menus() -> list[dict[str, Any]]:
    """Load menu records from disk and normalize older records."""
    with JSON_PATH.open("r", encoding="utf-8") as file:
        loaded = json.load(file)

    if not isinstance(loaded, list):
        raise ValueError(f"메뉴 데이터는 JSON 배열이어야 합니다: {JSON_PATH}")

    menus: list[dict[str, Any]] = []
    for item in loaded:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError(f"잘못된 메뉴 데이터가 있습니다: {item!r}")
        item.setdefault("recommendation", 0)
        menus.append(item)
    return menus


def save_menus() -> None:
    """Atomically persist menu data to avoid partially-written JSON files."""
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=JSON_PATH.parent,
            delete=False,
        ) as file:
            json.dump(menus, file, ensure_ascii=False, indent=4)
            file.write("\n")
            temp_path = Path(file.name)
        os.replace(temp_path, JSON_PATH)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


menus = load_menus()


def get_all() -> list[dict[str, Any]]:
    return menus


def search_word(word: str) -> list[dict[str, Any]]:
    """Search menu names without case sensitivity."""
    keyword = word.strip().casefold()
    if not keyword:
        return get_all()
    return [menu for menu in menus if keyword in str(menu.get("name", "")).casefold()]


# 기존 프런트엔드/호출 코드와의 호환성을 유지합니다.
def search_Word(word: str) -> list[dict[str, Any]]:
    return search_word(word)


def add_menu(menu: Any) -> dict[str, Any]:
    """Add a menu, assigning a unique ID on the server."""
    values = menu.model_dump() if hasattr(menu, "model_dump") else dict(menu)
    new_menu = {
        "id": max((item["id"] for item in menus), default=0) + 1,
        "name": values["name"],
        "calories": values["calories"],
        "description": values["description"],
        "recommendation": 0,
    }
    menus.append(new_menu)
    save_menus()
    return new_menu


def delete_menu(menu_id: int) -> int | None:
    for index, menu in enumerate(menus):
        if menu.get("id") == menu_id:
            deleted = menus.pop(index)
            save_menus()
            return deleted["id"]
    return None


def get_one(menu_id: int) -> dict[str, Any] | None:
    return next((menu for menu in menus if menu.get("id") == menu_id), None)


def update_one(menu_data: Any) -> dict[str, Any] | None:
    values = menu_data.model_dump() if hasattr(menu_data, "model_dump") else dict(menu_data)
    menu = get_one(values["id"])
    if menu is None:
        return None

    menu.update(
        name=values["name"],
        calories=values["calories"],
        description=values["description"],
    )
    save_menus()
    return menu


def update_recommend(menu_id: int) -> dict[str, Any] | None:
    menu = get_one(menu_id)
    if menu is None:
        return None

    menu["recommendation"] = int(menu.get("recommendation", 0)) + 1
    save_menus()
    return menu

    menu["recommendation"] = int(menu.get("recommendation", 0)) + 1
    save_menus()
    return menu