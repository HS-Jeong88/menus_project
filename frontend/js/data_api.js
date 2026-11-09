"use strict";

// 백엔드 주소가 다르면 이 값만 수정하세요.
const API_BASE_URL = "http://127.0.0.1:8000";

async function requestApi(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch (error) {
    throw new Error("서버에 연결할 수 없습니다. 서버 실행 상태를 확인해주세요.");
  }

  if (!response.ok) {
    let detail = "";

    try {
      const body = await response.json();
      detail = body.detail || body.message || "";
    } catch {
      // 응답 본문이 JSON이 아니거나 비어 있어도 기본 오류 메시지를 사용합니다.
    }

    throw new Error(detail || `요청에 실패했습니다. (HTTP ${response.status})`);
  }

  if (response.status === 204) return null;

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) return null;

  return response.json();
}

async function getAllMenus() {
  const result = await requestApi("/menus");

  if (!Array.isArray(result)) {
    throw new Error("서버에서 올바른 메뉴 목록을 받지 못했습니다.");
  }

  return result;
}

async function searchMenus(keyword) {
  const query = new URLSearchParams({ word: keyword });
  const result = await requestApi(`/menus/search?${query.toString()}`);

  if (!Array.isArray(result)) {
    throw new Error("서버에서 올바른 검색 결과를 받지 못했습니다.");
  }

  return result;
}

async function addMenu(menuObject) {
  return requestApi("/menus", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(menuObject),
  });
}

async function deleteMenu(menuId) {
  return requestApi(`/menus/${encodeURIComponent(menuId)}`, {
    method: "DELETE",
  });
}

async function getMenuOne(id) {
  return requestApi(`/menus/${encodeURIComponent(id)}`);
}

async function updateMenu(menuObject) {
  return requestApi("/menus", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(menuObject),
  });
}

async function recommendMenu(id) {
  return requestApi(`/menus/recommend/${encodeURIComponent(id)}`, { method: "POST" });
}
