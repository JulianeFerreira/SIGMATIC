from app.database import SessionLocal
from app.models import User


def main():
    db = SessionLocal()
    users = db.query(User).all()

    if not users:
        print("Nenhum usuário encontrado na tabela 'users'.")
    else:
        print("Usuários cadastrados:")
        for u in users:
            print(f"- id={u.id}, username={u.username}, email={u.email}, ativo={u.is_active}")

    db.close()


if __name__ == "__main__":
    main()
