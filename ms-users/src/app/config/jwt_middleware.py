from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config.jwt_service import JwtService

jwt_service = JwtService()

EXCLUDED_PATHS = [
    "/auth/login",
    "/auth/register",
    "/docs",
    "/redoc",
    "/openapi.json"
]

def add_jwt_middleware(app: FastAPI):
    @app.middleware("http")
    async def jwt_middleware(request: Request, call_next):
        print("Intercepted:", request.url.path)  
        if request.url.path in EXCLUDED_PATHS: 
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            print("Missing or invalid header")  
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Missing or invalid Authorization header"}
            )

        token = auth_header.split(" ")[1]
        result = jwt_service.verify_token(token)
        print("Verify result:", result) 

        if not result["valid"]:
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": result["error"]}
            )

        request.state.user = result["data"]
        return await call_next(request)
