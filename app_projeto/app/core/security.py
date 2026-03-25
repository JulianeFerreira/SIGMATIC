from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from ..database import get_db

SECRET_KEY = "Rs23RA45qwe"    # depois troque
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: str, expires_delta: int = 60):
    """
    subject = username (padrão do sistema)
    """
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ------------------------------------------------------------------
# Middleware – validar apenas usuários logados
# ------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        login: str = payload.get("sub")
        if not login:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    from ..crud import get_user_by_login
    user = get_user_by_login(db, login)

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    print(f"🟢 Usuário autenticado: {user.username}")
    return user
