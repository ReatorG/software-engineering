from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.auth.dto.login_request_dto import LoginRequestDto
from app.auth.dto.auth_response_dto import AuthResponseDto
from app.auth.dto.register_request_dto import RegisterRequestDto
from app.auth.domain.auth_service import AuthService
from app.database import get_db
from app.user.infrastructure.user_repository import UserRepository

router = APIRouter()


def get_auth_service(conn=Depends(get_db)) -> AuthService:
    repository = UserRepository(conn)
    return AuthService(repository)

@router.post("/register", response_model=AuthResponseDto)
def register_user(
    request: RegisterRequestDto,
    service: AuthService = Depends(get_auth_service)
):
    try:
        response = service.register(request)
        return JSONResponse(status_code=201, content=response.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/login", response_model=AuthResponseDto)
def login_user(
    request: LoginRequestDto,
    service: AuthService = Depends(get_auth_service)
):
    try:
        response = service.login(request)
        return JSONResponse(status_code=200, content=response.model_dump())
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
