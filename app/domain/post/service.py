from sqlalchemy import select  # SQLAlchemy 2.x 조회용 select 함수
from sqlalchemy.orm import Session  # DB 세션 타입
from fastapi import HTTPException, status  # 예외 응답과 상태 코드

from app.domain.post.models import Post  # Post ORM 모델
from app.domain.post.schemas import PostCreate, PostUpdate  # 게시글 생성/수정 스키마
from app.domain.user.models import User  # 작성자 정보를 위한 User ORM 모델


def create_post(db: Session, author: User, post_in: PostCreate) -> Post:  # 게시글 생성 서비스 함수
    new_post = Post(  # 새 Post ORM 객체 생성
        title=post_in.title,  # 요청 body의 title 저장
        content=post_in.content,  # 요청 body의 content 저장
        author_id=author.id,  # 현재 로그인한 유저 id를 작성자로 저장
    )

    db.add(new_post)  # 세션에 새 게시글 추가
    db.commit()  # DB에 실제 반영
    db.refresh(new_post)  # DB가 채운 값(id, created_at, updated_at)을 다시 읽어옴

    return new_post  # 생성된 게시글 반환


def list_posts(db: Session, limit: int, offset: int) -> list[Post]:  # 게시글 목록 조회 함수
    posts = db.scalars(  # ORM 객체 목록 조회
        select(Post)  # posts 테이블 조회
        .order_by(Post.id.desc())  # 최신 글이 먼저 오도록 id 내림차순 정렬
        .limit(limit)  # limit 개수만큼만 가져오기
        .offset(offset)  # offset 만큼 건너뛰기
    ).all()  # 결과를 리스트로 변환

    return posts  # 게시글 목록 반환


def get_post_or_404(db: Session, post_id: int) -> Post:  # 게시글 하나를 찾거나 없으면 404 예외 발생
    post = db.get(Post, post_id)  # 기본키(id)로 게시글 조회

    if post is None:  # 해당 id의 게시글이 없으면
        raise HTTPException(  # 404 Not Found 예외 발생
            status_code=status.HTTP_404_NOT_FOUND,  # 찾을 수 없음 상태 코드
            detail="게시글을 찾을 수 없습니다.",  # 에러 메시지
        )

    return post  # 찾은 게시글 반환


def ensure_post_owner(current_user: User, post: Post) -> None:  # 현재 유저가 이 게시글의 주인인지 검사
    if post.author_id != current_user.id:  # 게시글 작성자와 현재 유저가 다르면
        raise HTTPException(  # 403 Forbidden 예외 발생
            status_code=status.HTTP_403_FORBIDDEN,  # 접근 금지 상태 코드
            detail="본인 게시글만 수정/삭제할 수 있습니다.",  # 에러 메시지
        )


def update_post(db: Session, post: Post, post_in: PostUpdate) -> Post:  # 게시글 수정 함수
    update_data = post_in.model_dump(exclude_unset=True)  # 실제로 들어온 필드만 딕셔너리로 추출

    for field, value in update_data.items():  # 수정할 필드를 하나씩 순회
        setattr(post, field, value)  # ORM 객체의 해당 속성에 새 값 반영

    db.add(post)  # 수정된 객체를 세션에 반영
    db.commit()  # DB에 실제 반영
    db.refresh(post)  # updated_at 등 최신 상태를 다시 읽어옴

    return post  # 수정된 게시글 반환


def delete_post(db: Session, post: Post) -> None:  # 게시글 삭제 함수
    db.delete(post)  # 세션에서 게시글 삭제 예약
    db.commit()  # DB에 실제 삭제 반영