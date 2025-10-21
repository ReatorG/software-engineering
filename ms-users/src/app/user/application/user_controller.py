from fastapi import APIRouter, Depends, Query, status
from typing import Optional
import sqlite3

from app.database import get_db
from app.user.domain.user_service import UserService
from app.user.infrastructure.user_repository import UserRepository
from app.user.dto.create_user_request_dto import CreateUserRequest
from app.user.dto.update_user_request_dto import UpdateUserRequest
from app.user.dto.update_role_request_dto import UpdateRoleRequest
from app.user.dto.change_password_request_dto import ChangePasswordRequest
from app.user.dto.user_response_dto import UserResponse, UserListResponse
from app.config.role_guard import require_role


router = APIRouter()

def get_user_service(db: sqlite3.Connection = Depends(get_db)) -> UserService:
    repository = UserRepository(db)
    return UserService(repository)


#@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
#def create_user(
#    request: CreateUserRequest,
#    service: UserService = Depends(get_user_service)
#):
#    """
#    Crear un nuevo usuario
#    
#    Requiere:
#    - first_name: Nombre del usuario
#    - last_name: Apellido del usuario
#    - email: Email único
#    - password: Contraseña (mínimo 6 caracteres)
#    - role_id: ID del rol (3=ADMIN, 2=SUPERVISOR, 1=LEARNER)
#    """
#    user = service.create_user(request)
#    return UserResponse.model_validate(user)


@router.get("/", response_model=UserListResponse, dependencies=[require_role("ADMIN")])
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: UserService = Depends(get_user_service)
):
    """
    Listar todos los usuarios con paginación y filtros
    
    Filtros opcionales:
    - role_id: Filtrar por rol
    - is_active: Filtrar por estado activo
    """
    users, total = service.get_all_users(
        page=page, 
        page_size=page_size,
        role_id=role_id,
        is_active=is_active
    )
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """
    Obtener un usuario por ID
    """
    user = service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    service: UserService = Depends(get_user_service)
):
    """
    Actualizar información de un usuario
    
    Campos actualizables:
    - first_name
    - last_name
    - email
    """
    user = service.update_user(user_id, request)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserResponse, dependencies=[require_role("ADMIN")])
def update_user_role(
    user_id: int,
    request: UpdateRoleRequest,
    service: UserService = Depends(get_user_service)
):
    """
    Asignar o modificar el rol de un usuario
    
    Requiere:
    - role_id: ID del nuevo rol
    """
    user = service.assign_role(user_id, request)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/disable", response_model=UserResponse, dependencies=[require_role("ADMIN")])
def disable_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """
    Deshabilitar un usuario (soft delete)
    """
    user = service.disable_user(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/enable", response_model=UserResponse, dependencies=[require_role("ADMIN")])
def enable_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    """
    Habilitar un usuario previamente deshabilitado
    """
    user = service.enable_user(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/change-password", response_model=UserResponse)
def change_password(
    user_id: int,
    request: ChangePasswordRequest,
    service: UserService = Depends(get_user_service)
):
    """
    Cambiar contraseña del usuario

    Requiere:
    - current_password: Contraseña actual
    - new_password: Nueva contraseña (mínimo 6 caracteres)
    """
    user = service.change_password(user_id, request)
    return UserResponse.model_validate(user)
