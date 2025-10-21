import hashlib
from fastapi import HTTPException, status
from app.user.infrastructure.user_repository import UserRepository
from app.user.dto.create_user_request_dto import CreateUserRequest
from app.user.dto.update_user_request_dto import UpdateUserRequest
from app.user.dto.update_role_request_dto import UpdateRoleRequest
from app.user.dto.change_password_request_dto import ChangePasswordRequest
from typing import List, Optional, Dict, Any
from app.config.security_config import PasswordHasher

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
        self.hasher = PasswordHasher()

    def create_user(self, request: CreateUserRequest) -> Dict[str, Any]:
        """
        RN-0002: Gestión de Roles y Permisos
        - Cada usuario DEBE tener un rol asignado
        - Validar que el rol exista
        """
        # Validar que el email no esté registrado
        existing_user = self.repository.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # RN-0002: Validar que el rol exista
        role = self.repository.get_role_by_id(request.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        # Hash de la contraseña (RN-0006: Seguridad)
        hashed_password = self.hasher.hash(request.password)

        # Crear usuario
        user = self.repository.create_user(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=hashed_password,
            role_id=request.role_id
        )

        return user

    def get_user_by_id(self, user_id: int) -> Dict[str, Any]:
        """
        Obtener usuario por ID
        """
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def get_all_users(self, page: int = 1, page_size: int = 10,
                     role_id: Optional[int] = None,
                     is_active: Optional[bool] = None) -> tuple[List[Dict[str, Any]], int]:
        """
        Listar usuarios con filtros y paginación
        """
        skip = (page - 1) * page_size
        users = self.repository.get_all_users(
            skip=skip, 
            limit=page_size,
            role_id=role_id,
            is_active=is_active
        )
        total = self.repository.count_users(role_id=role_id, is_active=is_active)
        return users, total

    def update_user(self, user_id: int, request: UpdateUserRequest) -> Dict[str, Any]:
        """
        Actualizar información del usuario
        RN-0001: Solo usuarios activos pueden ser modificados
        """
        user = self.get_user_by_id(user_id)

        # RN-0001: Validar que el usuario esté activo
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify disabled user"
            )

        # Validar email único si se está cambiando
        if request.email and request.email != user['email']:
            existing_user = self.repository.get_user_by_email(request.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use"
                )

        # Actualizar solo los campos proporcionados
        update_data = request.model_dump(exclude_unset=True)
        updated_user = self.repository.update_user(user, **update_data)
        
        return updated_user

    def assign_role(self, user_id: int, request: UpdateRoleRequest) -> Dict[str, Any]:
        """
        RN-0002: Asignar/modificar rol del usuario
        - Validar que el rol sea válido
        """
        user = self.get_user_by_id(user_id)

        # Validar que el rol exista
        role = self.repository.get_role_by_id(request.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role_id"
            )

        updated_user = self.repository.update_user_role(user, request.role_id)
        return updated_user

    def disable_user(self, user_id: int) -> Dict[str, Any]:
        """
        Deshabilitar usuario (soft delete)
        """
        user = self.get_user_by_id(user_id)

        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already disabled"
            )

        disabled_user = self.repository.disable_user(user)
        return disabled_user

    def enable_user(self, user_id: int) -> Dict[str, Any]:
        """
        Habilitar usuario
        """
        user = self.get_user_by_id(user_id)

        if user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already enabled"
            )

        enabled_user = self.repository.enable_user(user)
        return enabled_user

    def change_password(self, user_id: int, request: ChangePasswordRequest) -> Dict[str, Any]:
        """
        Cambiar contraseña del usuario
        RN-0001: Solo usuarios activos pueden cambiar contraseña
        RN-0006: Validar contraseña actual antes de cambiar
        """
        user = self.get_user_by_id(user_id)

        # RN-0001: Validar que el usuario esté activo
        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change password for disabled user"
            )

        # RN-0006: Verificar contraseña actual
        if not self.hasher.verify(request.current_password, user['password']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Hash nueva contraseña
        new_hashed_password = self.hasher.hash(request.new_password)

        # Actualizar en BD
        cursor = self.repository.db.cursor()
        cursor.execute("""
            UPDATE usuarios SET password = ?, updated_at = ?
            WHERE id = ?
        """, (new_hashed_password, __import__('datetime').datetime.now().isoformat(), user['id']))
        self.repository.db.commit()

        return self.get_user_by_id(user_id)
