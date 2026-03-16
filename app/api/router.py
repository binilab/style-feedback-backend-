from fastapi import APIRouter  # 여러 하위 라우터를 묶기 위한 라우터 도구

from app.api.v1.admin import router as admin_router  # admin 라우터 가져오기
from app.api.v1.auth import router as auth_router  # auth 라우터 가져오기
from app.api.v1.comments import router as comments_router  # comments 라우터 가져오기
from app.api.v1.health import router as health_router  # health 라우터 가져오기
from app.api.v1.posts import router as posts_router  # posts 라우터 가져오기
from app.api.v1.users import router as users_router  # users 라우터 가져오기

api_router = APIRouter(prefix="/api/v1")  # 모든 API 앞에 /api/v1 공통 prefix 적용

api_router.include_router(health_router)  # health 라우터 등록
api_router.include_router(auth_router)  # auth 라우터 등록
api_router.include_router(admin_router)  # admin 라우터 등록
api_router.include_router(posts_router)  # posts 라우터 등록
api_router.include_router(comments_router)  # comments 라우터 등록
api_router.include_router(users_router)  # users 라우터 등록