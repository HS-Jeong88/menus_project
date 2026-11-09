"""FastAPI endpoints for the menu management application."""

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from service import data


a = FastAPI(title="메뉴 관리 API")


# 로컬 프런트엔드 개발 서버를 기본 허용합니다.
# 배포 시 MENU_CORS_ORIGINS 환경 변수에 허용할 origin을
# 쉼표로 구분해 지정하세요.
allowed_origins = os.getenv(
    "MENU_CORS_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500",
)

a.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in allowed_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class MenuCreate(BaseModel):
    """메뉴 등록 요청 모델. ID는 서버에서 생성합니다."""

    name: str = Field(min_length=1, max_length=100)
    calories: int = Field(ge=0)
    description: str = Field(max_length=1000)


class MenuUpdate(MenuCreate):
    """메뉴 수정 요청 모델."""

    id: int = Field(gt=0)


@a.get("/")
def home():
    return {"message": "환영합니다."}


@a.get("/짜장면")
def make_zzangmyeon():
    return {
        "message": "짜장면 여기 있어요",
        "cnt": 2,
    }


@a.get("/menus")
def get_menus():
    return data.get_all()


# /menus/{menu_id}보다 먼저 선언해 검색 경로가 ID 경로로 처리되지 않게 합니다.
@a.get("/menus/search")
def search_menus(word: str = ""):
    return data.search_word(word)


@a.post("/menus", status_code=201)
def add_menu(menu: MenuCreate):
    created_menu = data.add_menu(menu.model_dump())
    return {
        "message": "ok",
        "menu": created_menu,
    }


@a.delete("/menus/{menu_id}")
def delete_menu(menu_id: int):
    deleted_id = data.delete_menu(menu_id)

    if deleted_id is None:
        raise HTTPException(
            status_code=404,
            detail="메뉴를 찾을 수 없습니다.",
        )

    return {
        "message": "삭제했습니다.",
        "id": deleted_id,
    }


@a.get("/menus/{menu_id}")
def get_menu(menu_id: int):
    menu = data.get_one(menu_id)

    if menu is None:
        raise HTTPException(
            status_code=404,
            detail="메뉴를 찾을 수 없습니다.",
        )

    return menu


@a.put("/menus")
def update_menu(menu: MenuUpdate):
    updated_menu = data.update_one(menu.model_dump())

    if updated_menu is None:
        raise HTTPException(
            status_code=404,
            detail="메뉴를 찾을 수 없습니다.",
        )

    return {
        "message": "ok",
        "menu": updated_menu,
    }


@a.post("/menus/recommend/{menu_id}")
def recommend_menu(menu_id: int):
    updated_menu = data.update_recommend(menu_id)

    if updated_menu is None:
        raise HTTPException(
            status_code=404,
            detail="메뉴를 찾을 수 없습니다.",
        )

    return {
        "message": "ok",
        "recommendation": updated_menu["recommendation"],
    }