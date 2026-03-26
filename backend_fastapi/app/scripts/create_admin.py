from getpass import getpass

from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash  # usa a mesma função do login


def main():
    db = SessionLocal()

    username = input("Username do admin (ex: admin): ").strip() or "admin"
    email = input("Email do admin (opcional): ").strip() or None

    password = getpass("Senha para esse usuário: ").strip()

    hashed = get_password_hash(password)

    # Verifica se já existe usuário com esse username
    user = db.query(User).filter(User.username == username).first()

    if user:
        print(f"Atualizando usuário existente: {username}")
        user.hashed_password = hashed
        user.is_active = True
        user.is_superuser = True
    else:
        print(f"Criando novo usuário: {username}")
        user = User(
            username=username,
            full_name=username,
            email=email,
            hashed_password=hashed,
            is_active=True,
            is_superuser=True,
        )
        db.add(user)

    db.commit()
    db.close()
    print("Usuário admin criado/atualizado com sucesso.")


if __name__ == "__main__":
    main()
