from pydantic import BaseModel, EmailStr, Field ,ConfigDict
from datetime import datetime



class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="사용자 닉네임",
        examples=['wonbin']
    )

    email: EmailStr =Field(
        ...,
        description="사용자 이메일",
        examples=['wonbin@example.com'],
    )
    password: str= Field(
        ...,
        min_length=8,
        max_length=72,
        description='사용자 비밀번호',
        examples=['abc12345!']
    )


class UserResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    id: int 
    username: str 
    email : EmailStr
    created_at: datetime


    