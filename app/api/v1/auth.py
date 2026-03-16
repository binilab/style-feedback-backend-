from typing import Annotated  # Annotated 타입 힌트 사용

import jwt  # PyJWT 예외 처리를 위해 사용
from fastapi import APIRouter, Depends, HTTPException, status  # 라우터, 의존성 주입, 예외, 상태 코드
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Bearer 토큰 추출, 로그인 폼 처리
from sqlalchemy.orm import Session  # DB 세션 타입

from app.api.deps import get_db  # 요청마다 DB 세션을 주입하는 의존성
from app.core.security import create_access_token, decode_token  # JWT 생성/검증 유틸
from app.domain.user.models import User  # User ORM 모델
from app.domain.user.schemas import TokenResponse, UserCreate, UserResponse  # 요청/응답 스키마
from app.domain.user.service import authenticate_user, create_user, get_user_by_email  # 인증/회원가입 서비스 함수

router = APIRouter(prefix="/auth", tags=["auth"])  # /auth 경로를 담당하는 라우터 생성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")  # Authorization 헤더의 Bearer 토큰을 읽는 도구

DbSession = Annotated[Session, Depends(get_db)]  # DB 세션 의존성 타입 별칭
TokenDep = Annotated[str, Depends(oauth2_scheme)]  # Bearer 토큰 문자열 의존성 타입 별칭


def get_current_user(db: DbSession, token: TokenDep) -> User:  # 현재 로그인한 유저를 찾아주는 기본 인증 함수
    credentials_exception = HTTPException(  # 인증 실패 시 공통 예외 객체 생성
        status_code=status.HTTP_401_UNAUTHORIZED,  # 인증 실패 상태 코드
        detail="유효하지 않은 인증 정보입니다.",  # 에러 메시지
        headers={"WWW-Authenticate": "Bearer"},  # Bearer 인증 헤더 명시
    )

    try:  # JWT decode 과정에서 예외가 날 수 있으므로 try 블록 시작
        payload = decode_token(token)  # JWT 문자열을 검증/해석해서 payload 추출
        subject = payload.get("sub")  # payload에서 사용자 식별값(sub) 읽기

        if subject is None:  # sub가 없으면 정상 토큰으로 볼 수 없음
            raise credentials_exception  # 인증 실패 예외 발생
    except jwt.InvalidTokenError:  # 서명 불일치, 만료 등으로 토큰이 유효하지 않으면
        raise credentials_exception  # 인증 실패 예외 발생

    user = get_user_by_email(db, subject)  # sub로 저장한 이메일 기준으로 유저 조회

    if user is None:  # 토큰은 맞아도 해당 유저가 DB에 없으면
        raise credentials_exception  # 인증 실패 예외 발생

    return user  # 현재 로그인한 유저 ORM 객체 반환


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:  # 활성 계정만 통과시키는 함수
    if not current_user.is_active:  # 계정이 비활성 상태면
        raise HTTPException(  # 접근 거부 예외 발생
            status_code=status.HTTP_403_FORBIDDEN,  # 권한 없음 상태 코드
            detail="비활성화된 계정입니다.",  # 에러 메시지
        )

    return current_user  # 활성 계정이면 그대로 통과


def get_current_admin_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:  # 관리자만 통과시키는 함수
    if not current_user.is_admin:  # 관리자 권한이 없으면
        raise HTTPException(  # 접근 거부 예외 발생
            status_code=status.HTTP_403_FORBIDDEN,  # 권한 없음 상태 코드
            detail="관리자 권한이 필요합니다.",  # 에러 메시지
        )

    return current_user  # 관리자면 그대로 통과


CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]  # 활성 사용자 의존성 타입 별칭
CurrentAdminUser = Annotated[User, Depends(get_current_admin_user)]  # 관리자 사용자 의존성 타입 별칭


@router.post(
    "/signup",  # 최종 경로는 /auth/signup
    response_model=UserResponse,  # 응답은 UserResponse 형태로 반환
    status_code=status.HTTP_201_CREATED,  # 생성 성공 시 201 Created
)
def signup(user_in: UserCreate, db: DbSession):  # 회원가입 엔드포인트
    return create_user(db, user_in)  # 서비스 계층에서 유저 생성 후 반환


@router.post(
    "/login",  # 최종 경로는 /auth/login
    response_model=TokenResponse,  # 응답은 access_token과 token_type
)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):  # OAuth2 로그인 폼을 받음
    user = authenticate_user(  # 이메일(username 필드 사용)과 비밀번호로 로그인 검증
        db,  # DB 세션 전달
        form_data.username,  # OAuth2 폼의 username 필드에 이메일을 넣어 사용
        form_data.password,  # OAuth2 폼의 password 값 사용
    )

    if user is None:  # 이메일 또는 비밀번호가 틀리면
        raise HTTPException(  # 401 Unauthorized 예외 발생
            status_code=status.HTTP_401_UNAUTHORIZED,  # 인증 실패 상태 코드
            detail="이메일 또는 비밀번호가 올바르지 않습니다.",  # 에러 메시지
            headers={"WWW-Authenticate": "Bearer"},  # Bearer 인증 헤더 명시
        )

    access_token = create_access_token(user.email)  # 사용자 이메일을 sub로 넣어 JWT 발급

    return {  # 토큰 응답 반환
        "access_token": access_token,  # 발급된 access token
        "token_type": "bearer",  # 토큰 타입
    }


@router.get(
    "/me",  # 최종 경로는 /auth/me
    response_model=UserResponse,  # 현재 사용자 정보 반환
)
def read_me(current_user: CurrentActiveUser):  # 활성 상태의 현재 유저만 접근 가능
    return current_user  # 현재 로그인한 사용자 정보 반환