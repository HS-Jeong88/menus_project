"use strict";

// Set window.API_SERVER before loading this file to point at a separately
// deployed API, for example: window.API_SERVER = "https://api.example.com".
// Static browser JavaScript cannot read Render environment variables directly;
// inject this value through a config script or build-time substitution.
const API_SERVER = getApiServer();

function getApiServer() {
  const configuredServer = window.API_SERVER || window.MENU_API_BASE_URL;
  if (configuredServer) {
    return String(configuredServer).replace(/\/+$/, "");
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
    response = await fetch(`${API_SERVER}${path}`, options);
  } catch (error) {
    if (error.name === "AbortError") throw error;
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

  if (response.status === 204) return null;

  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) return null;
  return response.json();
}

async function getAllMenus(options = {}) {
  const result = await requestApi("/menus", options);

  if (!Array.isArray(result)) {
    throw new Error("서버에서 올바른 메뉴 목록을 받지 못했습니다.");
  }

  return result.filter((item) => item && typeof item === "object");
}

async function searchMenus(keyword, options = {}) {
  const query = new URLSearchParams({ word: keyword });
  const result = await requestApi(`/menus/search?${query.toString()}`, options);

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
  return requestApi(`/menus/${encodeURIComponent(menuId)}`, { method: "DELETE" });
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
