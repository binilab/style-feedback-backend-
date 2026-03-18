from __future__ import annotations  # 아직 나중에 정의되거나 import될 타입 이름을 문자열처럼 지연 평가하게 해줌

from datetime import datetime  # 생성 시각 타입으로 사용할 datetime 가져옴

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func  # 컬럼 타입, 외래키, 복합 유니크 제약, DB 함수 가져옴
from sqlalchemy.orm import Mapped, mapped_column, relationship  # SQLAlchemy 2.x ORM 필드/관계 선언 도구

from app.core.database import Base  # 모든 ORM 모델이 상속받는 공통 베이스 클래스


class PostLike(Base):  # post_likes 테이블과 연결될 ORM 클래스
    __tablename__ = "post_likes"  # 실제 DB 테이블 이름

    __table_args__ = (  # 테이블 수준 제약조건 설정
        UniqueConstraint("user_id", "post_id", name="uq_post_likes_user_post"),  # 같은 유저가 같은 글에 두 번 좋아요 못 누르게 막음
    )

    id: Mapped[int] = mapped_column(primary_key=True)  # 좋아요 기록 기본키 id

    user_id: Mapped[int] = mapped_column(  # 좋아요를 누른 유저 id
        ForeignKey("users.id", ondelete="CASCADE"),  # users.id 참조, 유저 삭제 시 좋아요 기록도 정리
        nullable=False,  # 유저 없는 좋아요는 허용하지 않음
        index=True,  # user_id 기준 조회 가능성이 있어 인덱스 추가
    )

    post_id: Mapped[int] = mapped_column(  # 어떤 게시글에 누른 좋아요인지 나타내는 게시글 id
        ForeignKey("posts.id", ondelete="CASCADE"),  # posts.id 참조, 게시글 삭제 시 좋아요 기록도 정리
        nullable=False,  # 게시글 없는 좋아요는 허용하지 않음
        index=True,  # post_id 기준 조회 가능성이 있어 인덱스 추가
    )

    created_at: Mapped[datetime] = mapped_column(  # 좋아요 생성 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # DB가 현재 시각을 기본값으로 넣음
        nullable=False,  # 필수값
    )

    user: Mapped["User"] = relationship(  # PostLike -> User 방향 ORM 관계
        back_populates="post_likes"  # User.post_likes 와 연결
    )

    post: Mapped["Post"] = relationship(  # PostLike -> Post 방향 ORM 관계
        back_populates="likes"  # Post.likes 와 연결
    )

    comments: Mapped[list["Comment"]] = relationship(  # User -> Comment 방향 ORM 관계
        back_populates="author"  # Comment.author 와 연결
    )