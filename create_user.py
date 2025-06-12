from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import re


app = create_app()

def senha_valida(senha):
    return (
        len(senha) >= 8 and
        re.search(r"[A-Za-z]", senha) and
        re.search(r"\d", senha) and
        re.search(r"[!@#$%&*\-_=+]", senha)
    )


from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash
import re

app = create_app()

def senha_valida(senha):
    return (
        len(senha) >= 8 and
        re.search(r"[A-Za-z]", senha) and
        re.search(r"\d", senha) and
        re.search(r"[!@#$%&*\-_=+]", senha)
    )

with app.app_context():
    username = input("Digite o nome de usuário: ").strip()
    email = input("Digite o e-mail: ").strip()
    password = input("Digite a senha: ").strip()
    confirm = input("Confirme a senha: ").strip()

    if password != confirm:
        print("A senha informada não corresponde com a confirmação de senha.")
    elif not senha_valida(password):
        print("A senha deve ter pelo menos 8 caracteres, incluir uma letra, um número e um caractere especial (!@#$%&*-_+=).")
    else:
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        print(f"Usuário '{username}' criado com sucesso!")


