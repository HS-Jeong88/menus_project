"""JSON-backed storage and menu operations."""

import json
import os
import tempfile
import threading
from pathlib import Path
from typing import Any


JSON_PATH = Path(__file__).resolve().parent.parent / "storage" / "menus_recommendation.json"
_lock = threading.RLock()


def load_menus() -> list[dict[str, Any]]:
    """Load menu records from disk, normalize older records, and validate them."""
    with JSON_PATH.open("r", encoding="utf-8") as file:
        loaded = json.load(file)

    if not isinstance(loaded, list):
        raise ValueError(f"메뉴 데이터는 JSON 배열이어야 합니다: {JSON_PATH}")

    menus: list[dict[str, Any]] = []
    seen_ids: set[int] = set()
    for index, item in enumerate(loaded):
        if not isinstance(item, dict):
            raise ValueError(f"{index + 1}번째 메뉴는 JSON 객체여야 합니다.")

        menu = dict(item)
        menu.setdefault("recommendation", 0)
        menu_id = menu.get("id")
        if type(menu_id) is not int or menu_id <= 0 or menu_id in seen_ids:
            raise ValueError(f"{index + 1}번째 메뉴의 ID가 잘못되었거나 중복됩니다: {menu_id!r}")
        if not isinstance(menu.get("name"), str) or not menu["name"].strip():
            raise ValueError(f"{index + 1}번째 메뉴의 이름이 올바르지 않습니다.")
        if type(menu.get("calories")) is not int or menu["calories"] < 0:
            raise ValueError(f"{index + 1}번째 메뉴의 칼로리가 올바르지 않습니다.")
        if not isinstance(menu.get("description"), str):
            raise ValueError(f"{index + 1}번째 메뉴의 설명이 문자열이 아닙니다.")
        if type(menu["recommendation"]) is not int or menu["recommendation"] < 0:
            raise ValueError(f"{index + 1}번째 메뉴의 추천 수가 올바르지 않습니다.")

        seen_ids.add(menu_id)
        menus.append(menu)
    return menus


def save_menus() -> None:
    """Atomically persist menu data to avoid partially-written JSON files."""
    with _lock:
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
    with _lock:
        return [dict(menu) for menu in menus]


def search_word(word: str) -> list[dict[str, Any]]:
    """Search menu names and descriptions without case sensitivity."""
    keyword = word.strip().casefold()
    snapshot = get_all()
    if not keyword:
        return snapshot
    return [
        menu
        for menu in snapshot
        if keyword in str(menu.get("name", "")).casefold()
        or keyword in str(menu.get("description", "")).casefold()
    ]


# 기존 프런트엔드/호출 코드와의 호환성을 유지합니다.
def search_Word(word: str) -> list[dict[str, Any]]:
    return search_word(word)


def add_menu(menu: Any) -> dict[str, Any]:
    """Add a menu, assigning a unique ID on the server."""
    values = menu.model_dump() if hasattr(menu, "model_dump") else dict(menu)
    with _lock:
        new_menu = {
            "id": max((item["id"] for item in menus), default=0) + 1,
            "name": values["name"],
            "calories": values["calories"],
            "description": values["description"],
            "recommendation": 0,
        }
        menus.append(new_menu)
        try:
            save_menus()
        except Exception:
            menus.pop()
            raise
        return dict(new_menu)


def delete_menu(menu_id: int) -> int | None:
    with _lock:
        for index, menu in enumerate(menus):
            if menu.get("id") == menu_id:
                deleted = menus.pop(index)
                try:
                    save_menus()
                except Exception:
                    menus.insert(index, deleted)
                    raise
                return deleted["id"]
    return None


def get_one(menu_id: int) -> dict[str, Any] | None:
    with _lock:
        menu = next((item for item in menus if item.get("id") == menu_id), None)
        return dict(menu) if menu is not None else None


def update_one(menu_data: Any) -> dict[str, Any] | None:
    values = menu_data.model_dump() if hasattr(menu_data, "model_dump") else dict(menu_data)
    with _lock:
        menu = next((item for item in menus if item.get("id") == values["id"]), None)
        if menu is None:
            return None

        previous = {key: menu[key] for key in ("name", "calories", "description")}
        menu.update(
            name=values["name"],
            calories=values["calories"],
            description=values["description"],
        )
        try:
            save_menus()
        except Exception:
            menu.update(previous)
            raise
        return dict(menu)


def update_recommend(menu_id: int) -> dict[str, Any] | None:
    with _lock:
        menu = next((item for item in menus if item.get("id") == menu_id), None)
        if menu is None:
            return None

        previous = menu.get("recommendation", 0)
        menu["recommendation"] = previous + 1
        try:
            save_menus()
        except Exception:
            menu["recommendation"] = previous
            raise
        return dict(menu)
