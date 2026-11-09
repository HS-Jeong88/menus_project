"""FastAPI endpoints for the menu management application."""

import logging
import os
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from service import data


logger = logging.getLogger(__name__)
a = FastAPI(title="메뉴 관리 API")

# Allow the local frontend development server by default. For deployment,
# set MENU_CORS_ORIGINS to a comma-separated list of trusted origins.
allowed_origins = os.getenv(
    "MENU_CORS_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500",
)
a.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip().rstrip("/")
        for origin in allowed_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


MenuName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
MenuDescription = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]


class MenuCreate(BaseModel):
    """Fields accepted when creating a menu; its ID is assigned by the server."""

    model_config = ConfigDict(extra="forbid")

    name: MenuName
    calories: int = Field(strict=True, ge=0)
    description: MenuDescription


class MenuUpdate(MenuCreate):
    """Fields accepted when updating a menu."""

    id: int = Field(strict=True, gt=0)


@a.exception_handler(data.StorageError)
async def storage_error_handler(_request: Request, exc: data.StorageError) -> JSONResponse:
    logger.exception("Menu storage operation failed", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "메뉴 데이터를 저장하지 못했습니다. 저장소 상태를 확인한 뒤 다시 시도해주세요."},
    )


@a.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    # Do not echo submitted values back to the client.
    errors = [
        {
            "field": ".".join(str(part) for part in error["loc"] if part != "body") or "request",
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": "요청 값이 올바르지 않습니다.", "errors": errors},
    )


@a.exception_handler(Exception)
async def unexpected_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled API error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
    )


@a.get("/")
def home():
    return {"message": "환영합니다."}


@a.get("/짜장면")
def make_zzangmyeon():
    return {"message": "짜장면 여기 있어요", "cnt": 2}


@a.get("/menus")
def get_menus():
    return data.get_all()


# Keep this static route before /menus/{menu_id}.
@a.get("/menus/search")
def search_menus(word: str = ""):
    return data.search_word(word)


@a.post("/menus", status_code=201)
def add_menu(menu: MenuCreate):
    created_menu = data.add_menu(menu.model_dump())
    return {"message": "ok", "menu": created_menu}


@a.delete("/menus/{menu_id}")
def delete_menu(menu_id: int = Path(gt=0)):
    deleted_id = data.delete_menu(menu_id)
    if deleted_id is None:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    return {"message": "삭제했습니다.", "id": deleted_id}


@a.get("/menus/{menu_id}")
def get_menu(menu_id: int = Path(gt=0)):
    menu = data.get_one(menu_id)
    if menu is None:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    return menu


@a.put("/menus")
def update_menu(menu: MenuUpdate):
    updated_menu = data.update_one(menu.model_dump())
    if updated_menu is None:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    return {"message": "ok", "menu": updated_menu}


@a.post("/menus/recommend/{menu_id}")
def recommend_menu(menu_id: int = Path(gt=0)):
    updated_menu = data.update_recommend(menu_id)
    if updated_menu is None:
        raise HTTPException(status_code=404, detail="메뉴를 찾을 수 없습니다.")
    return {"message": "ok", "recommendation": updated_menu["recommendation"]}
