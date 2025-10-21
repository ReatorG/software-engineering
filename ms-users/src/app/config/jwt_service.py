import jwt
from datetime import datetime, timedelta, timezone
from app.config.settings import settings


class JwtService:
    def generate_token(self, data: dict, expires_minutes: int = None):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str):
        if not token:
            return {"valid": False, "error": "Token is missing"}

        try:
            decoded = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return {"valid": True, "data": decoded}

        except jwt.ExpiredSignatureError:
            return {"valid": False, "error": "Token has expired"}
        except jwt.InvalidSignatureError:
            return {"valid": False, "error": "Invalid token signature"}
        except jwt.DecodeError:
            return {"valid": False, "error": "Malformed token"}
        except Exception as e:
            return {"valid": False, "error": f"Unexpected error: {str(e)}"}
