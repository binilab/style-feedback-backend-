from __future__ import annotations  # 아직 나중에 정의되거나 import될 타입 이름을 문자열처럼 지연 평가하게 해줌

from datetime import datetime  # 생성/수정 시각 타입으로 사용할 datetime 가져옴

from sqlalchemy import DateTime, ForeignKey, Text, func  # 컬럼 타입, 외래키, DB 함수 가져옴
from sqlalchemy.orm import Mapped, mapped_column, relationship  # SQLAlchemy 2.x ORM 필드/관계 선언 도구

from app.core.database import Base  # 모든 ORM 모델이 상속받는 공통 베이스 클래스


class Comment(Base):  # comments 테이블과 연결될 ORM 클래스
    __tablename__ = "comments"  # 실제 DB 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True)  # 댓글 기본키 id

    content: Mapped[str] = mapped_column(  # 댓글 본문 컬럼
        Text,  # 길 수 있으므로 Text 사용
        nullable=False,  # 댓글 내용은 필수값
    )

    post_id: Mapped[int] = mapped_column(  # 어느 게시글에 달린 댓글인지 나타내는 외래키
        ForeignKey("posts.id", ondelete="CASCADE"),  # posts.id를 참조하고, 게시글 삭제 시 댓글도 함께 정리
        nullable=False,  # 게시글 없는 댓글은 허용하지 않음
        index=True,  # post_id로 댓글 목록 조회를 자주 할 것이므로 인덱스 추가
    )

    author_id: Mapped[int] = mapped_column(  # 댓글 작성자 user의 id를 담는 외래키
        ForeignKey("users.id", ondelete="CASCADE"),  # users.id를 참조하고, 유저 삭제 시 댓글도 함께 정리
        nullable=False,  # 작성자 없는 댓글은 허용하지 않음
        index=True,  # author_id 기준 조회 가능성이 있어 인덱스 추가
    )

    created_at: Mapped[datetime] = mapped_column(  # 댓글 생성 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # DB가 현재 시각을 기본값으로 넣음
        nullable=False,  # 필수값
    )

    updated_at: Mapped[datetime] = mapped_column(  # 댓글 수정 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # 처음 생성 시 현재 시각을 넣음
        onupdate=func.now(),  # 수정 시 현재 시각으로 갱신
        nullable=False,  # 필수값
    )

    post: Mapped["Post"] = relationship(  # Comment -> Post 방향 ORM 관계
        back_populates="comments"  # Post.comments 와 서로 연결됨
    )

    author: Mapped["User"] = relationship(  # Comment -> User 방향 ORM 관계
        back_populates="comments"  # User.comments 와 서로 연결됨
    )