from fastapi import Depends, HTTPException, Request, status

def require_role(*allowed_roles: str):
    """
    Dependency que asegura que el usuario tenga al menos uno de los roles permitidos.
    Uso: dependencies=[require_role("ADMIN")]
    """
    def role_checker(request: Request):
        user = getattr(request.state, "user", None)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        role = user.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    return Depends(role_checker)
