"""JSON 기반 메뉴 데이터 저장 및 처리."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any


# 현재 작업 디렉터리가 아니라 이 파일의 위치를 기준으로 경로를 만듭니다.
JSON_PATH = (
    Path(__file__).resolve().parent.parent
    / "storage"
    / "menus_recommendation.json"
)


def load_menus() -> list[dict[str, Any]]:
    """JSON 파일에서 메뉴를 읽고 이전 데이터 형식도 보정합니다."""
    with JSON_PATH.open("r", encoding="utf-8") as file:
        loaded = json.load(file)

    if not isinstance(loaded, list):
        raise ValueError(f"메뉴 데이터는 JSON 배열이어야 합니다: {JSON_PATH}")

    menus: list[dict[str, Any]] = []

    for item in loaded:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError(f"잘못된 메뉴 데이터가 있습니다: {item!r}")

        # recommendation 항목이 없는 기존 데이터도 처리합니다.
        item.setdefault("recommendation", 0)
        menus.append(item)

    return menus


def save_menus() -> None:
    """JSON 파일을 임시 파일에 쓴 뒤 교체해 불완전한 저장을 방지합니다."""
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
    """메뉴 이름을 대소문자 구분 없이 검색합니다."""
    keyword = word.strip().casefold()

    if not keyword:
        return get_all()

    return [
        menu
        for menu in menus
        if keyword in str(menu.get("name", "")).casefold()
    ]


# 기존 함수명을 사용 중인 코드와의 호환성을 유지합니다.
def search_Word(word: str) -> list[dict[str, Any]]:
    return search_word(word)


def add_menu(menu: Any) -> dict[str, Any]:
    """메뉴를 추가하고 서버에서 고유 ID를 할당합니다."""
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
            deleted_menu = menus.pop(index)
            save_menus()
            return deleted_menu["id"]

    return None


def get_one(menu_id: int) -> dict[str, Any] | None:
    return next(
        (menu for menu in menus if menu.get("id") == menu_id),
        None,
    )


def update_one(menu_data: Any) -> dict[str, Any] | None:
    values = (
        menu_data.model_dump()
        if hasattr(menu_data, "model_dump")
        else dict(menu_data)
    )

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