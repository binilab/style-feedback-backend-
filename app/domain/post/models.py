from __future__ import annotations  # 앞으로 나올 타입 이름을 문자열처럼 지연 평가하게 해줌

from datetime import datetime  # 생성/수정 시각 타입으로 사용할 datetime 가져옴

from sqlalchemy import DateTime, ForeignKey, String, Text, func  # 컬럼 타입, 외래키, DB 함수 가져옴
from sqlalchemy.orm import Mapped, mapped_column, relationship  # SQLAlchemy 2.x ORM 필드/관계 선언 도구

from app.core.database import Base  # 모든 ORM 모델이 상속받는 공통 베이스 클래스


class Post(Base):  # posts 테이블과 연결될 ORM 클래스
    __tablename__ = "posts"  # 실제 DB 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True)  # 게시글 기본키 id
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # 게시글 제목
    content: Mapped[str] = mapped_column(Text, nullable=False)  # 게시글 본문

    author_id: Mapped[int] = mapped_column(  # 작성자 user의 id를 담는 외래키 컬럼
        ForeignKey("users.id", ondelete="CASCADE"),  # users.id 참조
        nullable=False,  # 작성자 없는 게시글 불가
        index=True,  # author_id 조회용 인덱스
    )

    created_at: Mapped[datetime] = mapped_column(  # 생성 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # DB가 현재 시각 기본값 넣기
        nullable=False,  # 필수값
    )
    updated_at: Mapped[datetime] = mapped_column(  # 수정 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # 처음 생성 시 현재 시각
        onupdate=func.now(),  # 수정 시 현재 시각으로 갱신
        nullable=False,  # 필수값
    )

    author: Mapped["User"] = relationship(  # Post -> User 방향 ORM 관계
        back_populates="posts"  # User.posts 와 연결
    )

    comments: Mapped[list["Comment"]] = relationship(  # Post -> Comment 방향 ORM 관계
        back_populates="post"  # Comment.post 와 연결
    )