from sqlalchemy import select  # SQLAlchemy 2.x 조회용 select 함수
from sqlalchemy.orm import Session  # DB 세션 타입
from fastapi import HTTPException, status  # 예외 응답과 상태 코드

from app.domain.comment.models import Comment  # Comment ORM 모델
from app.domain.comment.schemas import CommentCreate, CommentUpdate  # 댓글 생성/수정 스키마
from app.domain.post.models import Post  # Post ORM 모델
from app.domain.user.models import User  # User ORM 모델


def get_post_or_404(db: Session, post_id: int) -> Post:  # 게시글 존재 여부를 확인하는 함수
    post = db.get(Post, post_id)  # 기본키로 게시글 조회

    if post is None:  # 해당 id의 게시글이 없으면
        raise HTTPException(  # 404 예외 발생
            status_code=status.HTTP_404_NOT_FOUND,  # 찾을 수 없음 상태 코드
            detail="게시글을 찾을 수 없습니다.",  # 에러 메시지
        )

    return post  # 찾은 게시글 반환


def create_comment(db: Session, post: Post, author: User, comment_in: CommentCreate) -> Comment:  # 댓글 생성 서비스 함수
    new_comment = Comment(  # 새 Comment ORM 객체 생성
        content=comment_in.content,  # 요청 body의 댓글 내용 저장
        post_id=post.id,  # 어느 게시글에 달렸는지 저장
        author_id=author.id,  # 현재 로그인한 유저를 작성자로 저장
    )

    db.add(new_comment)  # 세션에 새 댓글 추가
    db.commit()  # DB에 실제 반영
    db.refresh(new_comment)  # DB가 채운 값(id, created_at, updated_at)을 다시 읽어옴

    return new_comment  # 생성된 댓글 반환


def list_comments_by_post(db: Session, post_id: int) -> list[Comment]:  # 특정 게시글의 댓글 목록 조회 함수
    comments = db.scalars(  # ORM 객체 목록 조회
        select(Comment)  # comments 테이블 조회
        .where(Comment.post_id == post_id)  # 해당 게시글에 속한 댓글만 필터링
        .order_by(Comment.id.asc())  # 오래된 댓글부터 보이도록 오름차순 정렬
    ).all()  # 결과를 리스트로 변환

    return comments  # 댓글 목록 반환


def get_comment_or_404(db: Session, comment_id: int) -> Comment:  # 댓글 하나를 찾거나 없으면 404 예외 발생
    comment = db.get(Comment, comment_id)  # 기본키로 댓글 조회

    if comment is None:  # 댓글이 없으면
        raise HTTPException(  # 404 예외 발생
            status_code=status.HTTP_404_NOT_FOUND,  # 찾을 수 없음 상태 코드
            detail="댓글을 찾을 수 없습니다.",  # 에러 메시지
        )

    return comment  # 찾은 댓글 반환


def ensure_comment_owner(current_user: User, comment: Comment) -> None:  # 현재 유저가 댓글 주인인지 검사
    if comment.author_id != current_user.id:  # 댓글 작성자와 현재 유저가 다르면
        raise HTTPException(  # 403 예외 발생
            status_code=status.HTTP_403_FORBIDDEN,  # 접근 금지 상태 코드
            detail="본인 댓글만 수정/삭제할 수 있습니다.",  # 에러 메시지
        )


def update_comment(db: Session, comment: Comment, comment_in: CommentUpdate) -> Comment:  # 댓글 수정 함수
    comment.content = comment_in.content  # 댓글 내용을 새 값으로 변경

    db.add(comment)  # 수정된 댓글 객체를 세션에 반영
    db.commit()  # DB에 실제 반영
    db.refresh(comment)  # updated_at 등 최신 상태를 다시 읽어옴

    return comment  # 수정된 댓글 반환


def delete_comment(db: Session, comment: Comment) -> None:  # 댓글 삭제 함수
    db.delete(comment)  # 세션에서 댓글 삭제 예약
    db.commit()  # DB에 실제 삭제 반영