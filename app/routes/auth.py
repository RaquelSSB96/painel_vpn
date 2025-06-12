from app import db
from app import mail
from app.models import User
from flask_mail import Message
from flask_login import login_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import re

auth = Blueprint('auth', __name__)

def generate_token(email):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'chave-padrao-para-desenvolvimento'))
    return serializer.dumps(email, salt='recover-password')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'chave-padrao-para-desenvolvimento'))
    try:
        email = serializer.loads(token, salt='recover-password', max_age=expiration)
    except Exception:
        return None
    return email


@auth.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = User.query.filter_by(username=username).first()

        if user:
            if not user.is_active:
                error = "Entre em contato com o administrador da rede."
            elif check_password_hash(user.password, password):
                login_user(user)  #faz login com Flask-Login

                #armazena info extra na session
                session["is_admin"] = user.is_admin

                #zera tentativas e salva
                user.login_attempts = 0
                db.session.commit()

                return redirect(url_for("dashboard.home"))
            else:
                user.login_attempts += 1
                if user.login_attempts >= 10:
                    user.is_active = False
                    error = "Usuário ou senha estão incorretos e seu acesso foi revogado após 10 tentativas."
                else:
                    error = "Usuário ou senha estão incorretos."
                db.session.commit()
        else:
            error = "Usuário ou senha estão incorretos."

    return render_template("login.html", error=error)

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))



@auth.route('/admin/cadastrar-funcionario')
def cadastrar_funcionario():
    if not session.get('is_admin'):
        return "Acesso negado", 403
    return render_template('cadastrar_funcionario.html')


@auth.route('/esqueci-senha', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_token(user.email)
            link = url_for('auth.reset_password', token=token, _external=True)

            msg = Message('Recuperação de senha - VPN Painel', sender=os.getenv('MAIL_USERNAME'), recipients=[email])
            msg.body = f"Olá, clique no link abaixo para redefinir sua senha:\n\n{link}\n\nEsse link expira em 30 minutos."

            try:
                mail.send(msg)
                return render_template('forgot_password.html', message="E-mail de recuperação enviado com sucesso!")
            except Exception as e:
                return render_template('forgot_password.html', error=f"Erro ao enviar e-mail: {str(e)}")

        else:
            return render_template('forgot_password.html', error="E-mail não encontrado.")
    return render_template('forgot_password.html')


def senha_valida(senha):
    return (
        len(senha) >= 8 and
        re.search(r"[A-Za-z]", senha) and
        re.search(r"\d", senha) and
        re.search(r"[!@#$%&*\-_=+]", senha)
    )

@auth.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)
    if not email:
        flash('Link inválido ou expirado.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        if password != confirm:
            return render_template('reset_password.html', error="A senha informada não corresponde com a confirmação de senha.")

        if not senha_valida(password):
            return render_template('reset_password.html', error="A senha deve ter pelo menos 8 caracteres, incluir uma letra, um número e um caractere especial (!@#$%&*-_+=).")

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(password)
            db.session.commit()
            flash('Senha redefinida com sucesso!', 'success')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


   



