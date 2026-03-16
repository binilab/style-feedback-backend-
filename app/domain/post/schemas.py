from datetime import datetime  # 생성/수정 시각 응답용 타입
from pydantic import BaseModel, ConfigDict, Field  # BaseModel, ORM 응답 설정, 필드 제약


class PostCreate(BaseModel):  # 게시글 생성 요청 body 검증 스키마
    title: str = Field(  # 제목 필드는 문자열
        ...,  # 필수값
        min_length=1,  # 최소 1글자
        max_length=200,  # 최대 200글자
        description="게시글 제목",  # Swagger 설명
        examples=["오늘 코디 어떤가요?"],  # 예시 값
    )
    content: str = Field(  # 본문 필드는 문자열
        ...,  # 필수값
        min_length=1,  # 최소 1글자
        max_length=5000,  # 최대 5000글자
        description="게시글 본문",  # Swagger 설명
        examples=["블랙 자켓과 청바지 조합인데 피드백 부탁드려요."],  # 예시 값
    )


class PostUpdate(BaseModel):  # 게시글 수정 요청 body 검증 스키마 (부분 수정용)
    title: str | None = Field(  # 제목은 선택적으로 보낼 수 있음
        default=None,  # 안 보내도 됨
        min_length=1,  # 보내는 경우 최소 1글자
        max_length=200,  # 보내는 경우 최대 200글자
        description="수정할 게시글 제목",  # Swagger 설명
        examples=["수정된 제목입니다"],  # 예시 값
    )
    content: str | None = Field(  # 본문도 선택적으로 보낼 수 있음
        default=None,  # 안 보내도 됨
        min_length=1,  # 보내는 경우 최소 1글자
        max_length=5000,  # 보내는 경우 최대 5000글자
        description="수정할 게시글 본문",  # Swagger 설명
        examples=["내용을 조금 수정했습니다."],  # 예시 값
    )


class PostResponse(BaseModel):  # 게시글 응답 스키마
    model_config = ConfigDict(from_attributes=True)  # ORM 객체 속성에서 값 읽기 허용

    id: int  # 게시글 고유 번호
    title: str  # 게시글 제목
    content: str  # 게시글 본문
    author_id: int  # 작성자 유저 id
    created_at: datetime  # 생성 시각
    updated_at: datetime  # 수정 시각