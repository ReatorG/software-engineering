import hashlib

class PasswordHasher:
    def hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return self.hash(plain_password) == hashed_password
