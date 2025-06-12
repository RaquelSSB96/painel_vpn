from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import re

app = create_app()

def senha_valida(senha):
    if (len(senha) < 8 or
        not re.search(r'[A-Z]', senha) or
        not re.search(r'\d', senha) or
        not re.search(r'[!@#$%&*\-_=+.]', senha)):
        return False
    return True

with app.app_context():
    nome = input("Nome de usuário: ").strip()
    email = input("E-mail corporativo (ex: teste@yopmail.com): ").strip()

    while True:
        senha = input("Senha: ").strip()
        confirmar = input("Confirme a senha: ").strip()

        if senha != confirmar:
            print("A senha informada não corresponde com a confirmação.")
            continue
        if not senha_valida(senha):
            print("A senha deve ter no mínimo 8 caracteres, 1 letra maiúscula, 1 número e 1 caractere especial.")
            continue
        break

    senha_hash = generate_password_hash(senha)

    novo_admin = User(
        username=nome,
        email=email,
        password=senha_hash,
        is_admin=True,
        is_active=True
    )

    db.session.add(novo_admin)
    db.session.commit()
    print(f"✅ Administrador '{nome}' criado com sucesso!")
