# 음식 메뉴 관리 시스템

음식 메뉴를 조회하고 관리하는 간단한 웹 애플리케이션입니다. 브라우저에서 메뉴를 검색·등록·수정·삭제하고, 메뉴별 추천 횟수를 기록할 수 있습니다.

## 주요 기능

- 홈 화면에서 메뉴 중 최대 3개를 무작위로 추천
- 전체 메뉴 목록 조회 및 메뉴 이름 검색
- 메뉴 등록, 수정, 삭제
- 메뉴별 추천 횟수 증가
- JSON 파일에 메뉴 데이터 저장

## 기술 스택

- **백엔드:** Python, FastAPI, Pydantic, Uvicorn
- **프런트엔드:** HTML, CSS, JavaScript
- **저장소:** JSON 파일

## 프로젝트 구조

```text
.
├── backend/
│   ├── main.py                         # FastAPI 애플리케이션과 API
│   ├── requirements.txt                # Python 패키지 목록
│   ├── service/
│   │   └── data.py                     # 메뉴 조회 및 변경 로직
│   └── storage/
│       ├── menus.json
│       └── menus_recommendation.json   # 애플리케이션이 읽고 쓰는 메뉴 데이터
└── frontend/
    ├── index.html                      # 웹 화면
    └── js/
        └── data_api.js                 # 백엔드 API 호출
```

## 실행 방법

Python이 설치된 환경에서 실행합니다. 백엔드와 프런트엔드는 각각 별도의 터미널에서 실행하세요.

### 1. 백엔드 실행

프로젝트 루트에서 PowerShell을 열고 다음 명령을 실행합니다.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:a --reload --host 127.0.0.1 --port 8000
```

API 문서는 백엔드 실행 후 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)에서 확인할 수 있습니다.

> 메뉴 데이터 파일의 경로가 백엔드 작업 디렉터리를 기준으로 지정되어 있으므로, 반드시 `backend` 폴더에서 서버를 실행해야 합니다.

### 2. 프런트엔드 실행

새 터미널에서 프로젝트 루트 기준으로 다음 명령을 실행합니다.

```powershell
cd frontend
py -m http.server 5500
```

브라우저에서 [http://127.0.0.1:5500](http://127.0.0.1:5500)을 엽니다. 프런트엔드는 `http://127.0.0.1:8000`의 백엔드 API를 호출하므로 두 서버를 모두 실행해야 합니다.

## API

| 메서드   | 경로                          | 설명                |
| -------- | ----------------------------- | ------------------- |
| `GET`    | `/`                           | 서버 환영 메시지    |
| `GET`    | `/menus`                      | 메뉴 전체 조회      |
| `GET`    | `/menus/search?word={검색어}` | 메뉴 이름으로 검색  |
| `GET`    | `/menus/{id}`                 | ID로 메뉴 조회      |
| `POST`   | `/menus`                      | 메뉴 등록           |
| `PUT`    | `/menus`                      | 메뉴 수정           |
| `DELETE` | `/menus/{menu_id}`            | 메뉴 삭제           |
| `POST`   | `/menus/recommend/{id}`       | 메뉴 추천 횟수 증가 |

메뉴 등록 및 수정 요청 본문은 JSON 형식이며 `name`, `calories`, `description` 필드를 사용합니다. ID는 등록 시 서버에서 할당합니다.

## 데이터 저장

백엔드는 `backend/storage/menus_recommendation.json`을 시작할 때 읽고, 메뉴를 추가·수정·삭제하거나 추천 횟수가 변경될 때 해당 파일에 저장합니다. 파일을 직접 수정할 때는 유효한 JSON 형식과 기존 메뉴 데이터 구조를 유지하세요.
