from datetime import datetime  # 생성/수정 시각 응답용 타입
from pydantic import BaseModel, ConfigDict, Field  # BaseModel, ORM 응답 설정, 필드 제약


class CommentCreate(BaseModel):  # 댓글 생성 요청 body 검증 스키마
    content: str = Field(  # 댓글 본문 필드는 문자열
        ...,  # 필수값
        min_length=1,  # 최소 1글자
        max_length=2000,  # 최대 2000글자
        description="댓글 내용",  # Swagger 설명
        examples=["블랙 자켓이 정말 잘 어울려요."],  # 예시 값
    )


class CommentUpdate(BaseModel):  # 댓글 수정 요청 body 검증 스키마
    content: str = Field(  # 수정할 댓글 본문 필드는 문자열
        ...,  # 필수값
        min_length=1,  # 최소 1글자
        max_length=2000,  # 최대 2000글자
        description="수정할 댓글 내용",  # Swagger 설명
        examples=["신발만 다른 색으로 바꾸면 더 좋을 것 같아요."],  # 예시 값
    )


class CommentResponse(BaseModel):  # 댓글 응답 스키마
    model_config = ConfigDict(from_attributes=True)  # ORM 객체 속성에서 값 읽기 허용

    id: int  # 댓글 고유 번호
    content: str  # 댓글 내용
    post_id: int  # 어느 게시글에 달린 댓글인지
    author_id: int  # 댓글 작성자 유저 id
    created_at: datetime  # 생성 시각
    updated_at: datetime  # 수정 시각