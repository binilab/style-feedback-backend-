# Style Feedback Backend

FastAPI 기반 스타일 피드백 커뮤니티 백엔드입니다.
사용자 인증(JWT), 게시글/댓글 CRUD, 관리자 조회 API를 제공합니다.

## Overview

- Base path: `/api/v1`
- API docs: `http://localhost:8000/docs` (`/redoc`도 사용 가능)
- DB: PostgreSQL + SQLAlchemy 2.x
- Migration: Alembic

## Features

- Auth
  - `POST /api/v1/auth/signup`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
- Users
  - `POST /api/v1/users`
  - `GET /api/v1/users`
- Posts
  - `POST /api/v1/posts`
  - `GET /api/v1/posts`
  - `GET /api/v1/posts/{post_id}`
  - `PATCH /api/v1/posts/{post_id}`
  - `DELETE /api/v1/posts/{post_id}`
- Comments
  - `POST /api/v1/posts/{post_id}/comments`
  - `GET /api/v1/posts/{post_id}/comments`
  - `PATCH /api/v1/comments/{comment_id}`
  - `DELETE /api/v1/comments/{comment_id}`
- Admin
  - `GET /api/v1/admin/users` (관리자 권한 필요)
- Health
  - `GET /api/v1/health`

## Tech Stack

- Python 3.11+
- FastAPI / Uvicorn
- SQLAlchemy 2.x
- Alembic
- Pydantic / pydantic-settings
- PyJWT / pwdlib
- PostgreSQL (psycopg)

## Project Structure

```text
.
├── app
│   ├── api
│   │   ├── deps.py
│   │   ├── router.py
│   │   └── v1
│   │       ├── admin.py
│   │       ├── auth.py
│   │       ├── comments.py
│   │       ├── health.py
│   │       ├── posts.py
│   │       └── users.py
│   ├── core
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── domain
│   │   ├── comment
│   │   ├── like
│   │   ├── post
│   │   └── user
│   └── main.py
├── alembic
│   └── versions
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Local Setup

### 1) Python venv + dependency install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) PostgreSQL 실행

로컬 PostgreSQL을 직접 사용하거나 Docker Compose를 사용할 수 있습니다.

```bash
docker compose up -d db
```

### 3) Environment 변수 설정

`app/core/config.py` 기준으로 아래 값들을 사용합니다.

```dotenv
APP_NAME=STYLE FEEDBACK API
APP_VERSION=0.1.0
DEBUG=true

DATABASE_URL=postgresql+psycopg://style_user:style_password@localhost:5432/style_feedback

SECRET_KEY=change-this-to-a-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

실서비스에서는 `SECRET_KEY`를 반드시 강한 랜덤 값으로 변경하세요.

### 4) DB migration 적용

```bash
alembic upgrade head
```

### 5) 서버 실행

```bash
uvicorn app.main:app --reload
```

## Development Notes

- 라우터는 `app/api/router.py`에서 `/api/v1` prefix로 묶입니다.
- 인증은 Bearer JWT 기반이며, 로그인 후 받은 `access_token`을 사용합니다.
- Alembic 마이그레이션은 현재 users/posts/comments 기준으로 작성되어 있습니다.
- `app/domain/like` 모듈은 존재하지만, 현재 `app/api/router.py`에 likes 라우터가 연결되어 있지 않아 외부 API로 노출되지 않습니다.

## Migration Commands

```bash
# 새 revision 생성
alembic revision --autogenerate -m "your message"

# 최신 상태로 업그레이드
alembic upgrade head

# 한 단계 롤백
alembic downgrade -1
```

## Test Status

현재 `tests/` 디렉터리에 테스트 파일이 없습니다. 테스트를 추가할 경우 아래와 같이 실행할 수 있습니다.

```bash
pytest
```
