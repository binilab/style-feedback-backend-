from sqlalchemy import func, select  # 집계(count)와 SQLAlchemy 2.x select 함수
from sqlalchemy.exc import IntegrityError  # DB 유니크 제약 위반 같은 예외 처리용
from sqlalchemy.orm import Session  # DB 세션 타입
from fastapi import HTTPException, status  # 예외 응답과 상태 코드

from app.domain.like.models import PostLike  # PostLike ORM 모델
from app.domain.post.models import Post  # Post ORM 모델
from app.domain.user.models import User  # User ORM 모델


def get_post_or_404(db: Session, post_id: int) -> Post:  # 게시글 하나를 찾거나 없으면 404 예외 발생
    post = db.get(Post, post_id)  # 기본키(id)로 게시글 조회

    if post is None:  # 게시글이 없으면
        raise HTTPException(  # 404 예외 발생
            status_code=status.HTTP_404_NOT_FOUND,  # 찾을 수 없음 상태 코드
            detail="게시글을 찾을 수 없습니다.",  # 에러 메시지
        )

    return post  # 찾은 게시글 반환


def get_like_by_user_and_post(db: Session, user_id: int, post_id: int) -> PostLike | None:  # 특정 유저-게시글 좋아요 기록 조회
    return db.scalar(  # 첫 번째 결과 하나 또는 None 반환
        select(PostLike).where(  # post_likes 테이블 조회
            PostLike.user_id == user_id,  # 유저 id가 일치하고
            PostLike.post_id == post_id,  # 게시글 id도 일치하는 좋아요 기록 찾기
        )
    )


def create_like(db: Session, current_user: User, post_id: int) -> None:  # 게시글 좋아요 생성 함수
    get_post_or_404(db, post_id)  # 대상 게시글 존재 여부 먼저 확인

    existing_like = get_like_by_user_and_post(db, current_user.id, post_id)  # 이미 좋아요 눌렀는지 확인

    if existing_like is not None:  # 이미 눌렀다면
        raise HTTPException(  # 409 Conflict 예외 발생
            status_code=status.HTTP_409_CONFLICT,  # 중복 충돌 상태 코드
            detail="이미 좋아요를 눌렀습니다.",  # 에러 메시지
        )

    new_like = PostLike(  # 새 좋아요 ORM 객체 생성
        user_id=current_user.id,  # 현재 로그인 유저 id 저장
        post_id=post_id,  # 대상 게시글 id 저장
    )

    db.add(new_like)  # 세션에 새 좋아요 추가

    try:  # DB 유니크 제약 위반 가능성이 있어 try 블록 시작
        db.commit()  # DB에 실제 반영
    except IntegrityError:  # 동시에 중복 요청이 들어와 유니크 제약에 걸리면
        db.rollback()  # 현재 트랜잭션 롤백
        raise HTTPException(  # 409 Conflict 예외 발생
            status_code=status.HTTP_409_CONFLICT,  # 중복 충돌 상태 코드
            detail="이미 좋아요를 눌렀습니다.",  # 에러 메시지
        )


def delete_like(db: Session, current_user: User, post_id: int) -> None:  # 게시글 좋아요 취소 함수
    get_post_or_404(db, post_id)  # 대상 게시글 존재 여부 먼저 확인

    like = get_like_by_user_and_post(db, current_user.id, post_id)  # 현재 유저의 좋아요 기록 조회

    if like is None:  # 좋아요 기록이 없으면
        raise HTTPException(  # 404 예외 발생
            status_code=status.HTTP_404_NOT_FOUND,  # 찾을 수 없음 상태 코드
            detail="좋아요 기록을 찾을 수 없습니다.",  # 에러 메시지
        )

    db.delete(like)  # 세션에서 좋아요 삭제 예약
    db.commit()  # DB에 실제 삭제 반영


def get_like_count(db: Session, post_id: int) -> int:  # 특정 게시글 좋아요 수 조회 함수
    get_post_or_404(db, post_id)  # 대상 게시글 존재 여부 먼저 확인

    like_count = db.scalar(  # count 집계 결과 하나 반환
        select(func.count(PostLike.id)).where(  # post_likes의 id 개수 세기
            PostLike.post_id == post_id  # 해당 게시글 id와 일치하는 좋아요만 필터링
        )
    )

    return like_count or 0  # None 방지를 위해 0 처리


def is_post_liked_by_user(db: Session, current_user: User, post_id: int) -> bool:  # 현재 유저가 게시글에 좋아요 눌렀는지 여부 확인
    get_post_or_404(db, post_id)  # 대상 게시글 존재 여부 먼저 확인

    like = get_like_by_user_and_post(db, current_user.id, post_id)  # 좋아요 기록 조회

    return like is not None  # 있으면 True, 없으면 False