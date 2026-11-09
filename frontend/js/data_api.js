"use strict";

// 개발 환경에서는 localhost의 8000번 포트를 사용하고,
// 배포 환경에서는 기본적으로 현재 페이지와 같은 origin을 사용합니다.
// API 서버가 별도 주소라면 페이지에서 data_api.js보다 먼저
// window.MENU_API_BASE_URL 값을 설정하세요.
const API_BASE_URL = getApiBaseUrl();

function getApiBaseUrl() {
  if (window.MENU_API_BASE_URL) {
    return window.MENU_API_BASE_URL.replace(/\/+$/, "");
  }

  const host = window.location.hostname;

  if (host === "localhost" || host === "127.0.0.1" || host === "") {
    return "http://127.0.0.1:8000";
  }

  return window.location.origin;
}

async function requestApi(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new Error("서버에 연결할 수 없습니다. 서버 주소와 실행 상태를 확인해주세요.");
  }

  if (!response.ok) {
    let message = "";

    try {
      const body = await response.json();
      const detail = body?.detail ?? body?.message;

      if (typeof detail === "string") {
        message = detail;
      } else if (detail != null) {
        message = JSON.stringify(detail);
      }
    } catch {
      // 오류 응답에 JSON 본문이 없을 수 있습니다.
    }

    throw new Error(message || `요청에 실패했습니다. (HTTP ${response.status})`);
  }

  // DELETE 등의 API는 응답 본문 없이 204를 반환할 수 있습니다.
  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    return null;
  }

  return response.json();
}

async function getAllMenus() {
  const result = await requestApi("/menus");

  if (!Array.isArray(result)) {
    throw new Error("서버에서 올바른 메뉴 목록을 받지 못했습니다.");
  }

  return result.filter((item) => item && typeof item === "object");
}

async function searchMenus(keyword) {
  const query = new URLSearchParams({ word: keyword });
  const result = await requestApi(`/menus/search?${query.toString()}`);

  if (!Array.isArray(result)) {
    throw new Error("서버에서 올바른 검색 결과를 받지 못했습니다.");
  }

  return result.filter((item) => item && typeof item === "object");
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
