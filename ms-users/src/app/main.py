from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from app.user.application.user_controller import router as user_router
from app.auth.application.auth_controller import router as auth_router
from app.config.cors_config import setup_cors
from app.config.jwt_middleware import add_jwt_middleware

security = HTTPBearer()  # solo para documentar/activar Authorize en Swagger

def create_app() -> FastAPI:
    app = FastAPI(
        title="MS-USERS",
        version="1.0.0",
        description="Microservice for user and auth management",
        swagger_ui_parameters={"persistAuthorization": True},
        openapi_tags=[
            {"name": "Users", "description": "User management endpoints"},
            {"name": "Auth", "description": "Authentication endpoints"},
        ],
    )

    setup_cors(app)
    add_jwt_middleware(app)

    
    app.include_router(
        user_router,
        prefix="/users",
        tags=["Users"],
        dependencies=[Depends(security)],   # <- activa Authorize para /users/*
    )
    
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])

    return app

app = create_app()
