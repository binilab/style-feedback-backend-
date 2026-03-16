from typing import Annotated  # Annotated 타입 힌트 사용

from fastapi import APIRouter, Depends, Response, status  # 라우터, 의존성 주입, 응답 객체, 상태 코드
from sqlalchemy.orm import Session  # DB 세션 타입

from app.api.deps import get_db  # DB 세션 의존성
from app.api.v1.auth import CurrentActiveUser  # 로그인 + 활성 계정 사용자 의존성
from app.domain.comment.schemas import CommentCreate, CommentResponse, CommentUpdate  # 댓글 요청/응답 스키마
from app.domain.comment.service import create_comment, delete_comment, ensure_comment_owner, get_comment_or_404, get_post_or_404, list_comments_by_post, update_comment  # 댓글 서비스 함수들

router = APIRouter(tags=["comments"])  # comments 관련 엔드포인트를 묶는 라우터 생성

DbSession = Annotated[Session, Depends(get_db)]  # DB 세션 의존성 타입 별칭


@router.post(
    "/posts/{post_id}/comments",  # 최종 경로는 /posts/{post_id}/comments
    response_model=CommentResponse,  # 응답은 CommentResponse 형태
    status_code=status.HTTP_201_CREATED,  # 생성 성공 시 201 Created
)
def create_comment_endpoint(
    post_id: int,  # 댓글을 달 게시글 id
    comment_in: CommentCreate,  # 댓글 생성 요청 body
    db: DbSession,  # DB 세션
    current_user: CurrentActiveUser,  # 로그인 + 활성 사용자
):  # 댓글 작성 엔드포인트
    post = get_post_or_404(db, post_id)  # 댓글 대상 게시글 존재 여부 확인
    return create_comment(db, post, current_user, comment_in)  # 게시글과 현재 사용자 기준으로 댓글 생성


@router.get(
    "/posts/{post_id}/comments",  # 최종 경로는 /posts/{post_id}/comments
    response_model=list[CommentResponse],  # 댓글 목록 응답
)
def list_comments_by_post_endpoint(post_id: int, db: DbSession):  # 특정 게시글 댓글 목록 조회 엔드포인트
    get_post_or_404(db, post_id)  # 게시글이 실제 존재하는지 먼저 확인
    return list_comments_by_post(db, post_id)  # 해당 게시글의 댓글 목록 반환


@router.patch(
    "/comments/{comment_id}",  # 최종 경로는 /comments/{comment_id}
    response_model=CommentResponse,  # 수정 후 댓글 응답
)
def update_comment_endpoint(
    comment_id: int,  # 수정할 댓글 id
    comment_in: CommentUpdate,  # 댓글 수정 요청 body
    db: DbSession,  # DB 세션
    current_user: CurrentActiveUser,  # 로그인 + 활성 사용자
):  # 댓글 수정 엔드포인트
    comment = get_comment_or_404(db, comment_id)  # 댓글 존재 여부 확인
    ensure_comment_owner(current_user, comment)  # 현재 사용자가 댓글 주인인지 검사
    return update_comment(db, comment, comment_in)  # 검사 통과 시 댓글 수정


@router.delete(
    "/comments/{comment_id}",  # 최종 경로는 /comments/{comment_id}
    status_code=status.HTTP_204_NO_CONTENT,  # 삭제 성공 시 204 No Content
)
def delete_comment_endpoint(
    comment_id: int,  # 삭제할 댓글 id
    db: DbSession,  # DB 세션
    current_user: CurrentActiveUser,  # 로그인 + 활성 사용자
):  # 댓글 삭제 엔드포인트
    comment = get_comment_or_404(db, comment_id)  # 댓글 존재 여부 확인
    ensure_comment_owner(current_user, comment)  # 현재 사용자가 댓글 주인인지 검사
    delete_comment(db, comment)  # 검사 통과 시 댓글 삭제
    return Response(status_code=status.HTTP_204_NO_CONTENT)  # 본문 없는 성공 응답 반환