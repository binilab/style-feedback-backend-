from typing import Annotated  # Annotated 타입 힌트 사용

from fastapi import APIRouter, Depends, Query, Response, status  # 라우터, 의존성 주입, 쿼리 파라미터, 응답 객체, 상태 코드
from sqlalchemy.orm import Session  # DB 세션 타입

from app.api.deps import get_db  # DB 세션 의존성
from app.api.v1.auth import CurrentActiveUser  # 로그인 + 활성 계정 사용자 의존성
from app.domain.post.schemas import PostCreate, PostResponse, PostUpdate  # 게시글 요청/응답 스키마
from app.domain.post.service import create_post, delete_post, ensure_post_owner, get_post_or_404, list_posts, update_post  # 게시글 서비스 함수들

router = APIRouter(prefix="/posts", tags=["posts"])  # /posts 경로를 담당하는 라우터 생성

DbSession = Annotated[Session, Depends(get_db)]  # DB 세션 의존성 타입 별칭


@router.post(
    "",  # 최종 경로는 /posts
    response_model=PostResponse,  # 응답은 PostResponse 형태
    status_code=status.HTTP_201_CREATED,  # 생성 성공 시 201 Created
)
def create_post_endpoint(post_in: PostCreate, db: DbSession, current_user: CurrentActiveUser):  # 게시글 작성 엔드포인트
    return create_post(db, current_user, post_in)  # 현재 로그인한 유저를 작성자로 하여 게시글 생성


@router.get(
    "",  # 최종 경로는 /posts
    response_model=list[PostResponse],  # 게시글 목록 응답
)
def list_posts_endpoint(
    db: DbSession,  # DB 세션
    limit: int = Query(default=20, ge=1, le=100),  # 한 번에 가져올 개수 (1~100)
    offset: int = Query(default=0, ge=0),  # 앞에서 몇 개를 건너뛸지
):  # 게시글 목록 조회 엔드포인트
    return list_posts(db, limit, offset)  # limit/offset 기반 목록 조회


@router.get(
    "/{post_id}",  # 최종 경로는 /posts/{post_id}
    response_model=PostResponse,  # 게시글 상세 응답
)
def read_post_endpoint(post_id: int, db: DbSession):  # 게시글 상세 조회 엔드포인트
    return get_post_or_404(db, post_id)  # 없으면 404, 있으면 게시글 반환


@router.patch(
    "/{post_id}",  # 최종 경로는 /posts/{post_id}
    response_model=PostResponse,  # 수정 후 게시글 응답
)
def update_post_endpoint(
    post_id: int,  # 수정할 게시글 id
    post_in: PostUpdate,  # 수정 요청 body
    db: DbSession,  # DB 세션
    current_user: CurrentActiveUser,  # 로그인 + 활성 사용자
):  # 게시글 수정 엔드포인트
    post = get_post_or_404(db, post_id)  # 먼저 게시글 존재 여부 확인
    ensure_post_owner(current_user, post)  # 현재 사용자가 글 주인인지 검사
    return update_post(db, post, post_in)  # 검사 통과 시 게시글 수정


@router.delete(
    "/{post_id}",  # 최종 경로는 /posts/{post_id}
    status_code=status.HTTP_204_NO_CONTENT,  # 삭제 성공 시 204 No Content
)
def delete_post_endpoint(
    post_id: int,  # 삭제할 게시글 id
    db: DbSession,  # DB 세션
    current_user: CurrentActiveUser,  # 로그인 + 활성 사용자
):  # 게시글 삭제 엔드포인트
    post = get_post_or_404(db, post_id)  # 먼저 게시글 존재 여부 확인
    ensure_post_owner(current_user, post)  # 현재 사용자가 글 주인인지 검사
    delete_post(db, post)  # 검사 통과 시 게시글 삭제
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # 본문 없는 성공 응답 반환