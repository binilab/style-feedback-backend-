from __future__ import annotations  # 앞으로 나올 타입 이름을 문자열처럼 지연 평가하게 해줌

from datetime import datetime  # 생성 시각 타입으로 사용할 datetime 가져옴

from sqlalchemy import Boolean, DateTime, String, func  # 컬럼 타입과 DB 함수 가져옴
from sqlalchemy.orm import Mapped, mapped_column, relationship  # SQLAlchemy 2.x ORM 필드/관계 선언 도구

from app.core.database import Base  # 모든 ORM 모델의 공통 베이스 클래스


class User(Base):  # users 테이블과 연결될 ORM 클래스
    __tablename__ = "users"  # 실제 DB 테이블 이름

    id: Mapped[int] = mapped_column(primary_key=True)  # 기본키 id
    username: Mapped[str] = mapped_column(String(20), nullable=False)  # 닉네임, 필수값
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)  # 이메일, 중복 금지 + 인덱스
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)  # 해시된 비밀번호 저장용 컬럼

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")  # 계정 활성 여부
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")  # 관리자 여부

    created_at: Mapped[datetime] = mapped_column(  # 생성 시각 컬럼
        DateTime(timezone=True),  # 타임존 포함 datetime 타입
        server_default=func.now(),  # DB가 현재 시각을 기본값으로 넣음
        nullable=False,  # 필수값
    )

    posts: Mapped[list["Post"]] = relationship(  # User -> Post 방향 ORM 관계
        back_populates="author"  # Post.author 와 서로 연결됨
    )