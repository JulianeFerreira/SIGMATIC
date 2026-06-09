from fastapi import Depends, HTTPException, status

# no futuro: pegar usuário logado, etc.
def get_current_user():
    # MOCK: sempre "admin". Trocar por autenticação de verdade.
    return {"username": "admin", "role": "administrador"}


def require_role(roles: list[str]):
    def dependency(user=Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente",
            )
        return user

    return dependency
