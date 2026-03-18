from pydantic import BaseModel  # 응답 스키마 정의용 BaseModel


class LikeCountResponse(BaseModel):  # 좋아요 수 응답 스키마
    post_id: int  # 대상 게시글 id
    like_count: int  # 해당 게시글의 좋아요 수


class MyLikeStatusResponse(BaseModel):  # 내가 좋아요 눌렀는지 여부 응답 스키마
    post_id: int  # 대상 게시글 id
    liked: bool  # 현재 로그인 사용자가 좋아요를 눌렀는지 여부