from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from ..database import get_db
from .. import crud
from ..core.security import verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", include_in_schema=False, response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("usuarios/login.html", {"request": request})


@router.get("/register", include_in_schema=False, response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("usuarios/register.html", {"request": request})


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Debug (se quiser, pode remover depois)
    print("🟢 LOGIN RECEBIDO:", form_data.username, form_data.password)

    # Aceita login por username OU email
    user = crud.get_user_by_login(db, form_data.username)

    if not user:
        print("🔴 Usuário NÃO encontrado:", form_data.username)
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    print("🟢 Usuário encontrado:", user.username, "-", user.email)

    # Valida pelo hashed_password (NÃO usar user.password)
    if not getattr(user, "hashed_password", None):
        print("🔴 Usuário sem hashed_password:", user.username)
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    if not verify_password(form_data.password, user.hashed_password):
        print("🔴 Senha incorreta para:", user.username)
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    print("🟢 LOGIN OK → Token gerado")

    # Token padronizado com username no "sub"
    token = create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register")
def register_user(data: dict, db: Session = Depends(get_db)):
    return crud.create_user(db, data)
