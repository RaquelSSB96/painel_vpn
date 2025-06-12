from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from app.models import User, CertificadoVPN
from app import db
from werkzeug.security import generate_password_hash
from app.services.vpn_generator import gerar_vpn_para_usuario
from flask_login import current_user, login_required
import re

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
def home():
    return render_template('dashboard.html')

@bp.route('/cadastrar', methods=['POST'])
def cadastrar_funcionario():
    if not session.get("is_admin"):
        flash("Acesso negado!", "danger")
        return redirect(url_for("dashboard.home"))

    nome = request.form.get("nome", "").strip()
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip()
    senha = request.form.get("senha", "").strip()
    confirmar = request.form.get("confirmar_senha", "").strip()
    is_admin = True if request.form.get("is_admin") else False

    erros = []

    if not nome:
        erros.append("Por favor informe NOME.")
    if not username:
        erros.append("Por favor informe USUÁRIO.")
    if not email or not email.endswith("@yopmail.com"):
        erros.append("E-mail inválido ou não é corporativo (@yopmail.com).")
    if senha != confirmar:
        erros.append("A senha informada não corresponde com a confirmação de senha.")
    if len(senha) < 8 or not re.search(r'[A-Z]', senha) or not re.search(r'\d', senha) or not re.search(r'[!@#$%&*\-_=+]', senha):
        erros.append("A senha deve ter no mínimo 8 caracteres, 1 letra maiúscula, 1 número e 1 símbolo especial.")

    if erros:
        for erro in erros:
            flash(erro, "danger")
        return redirect(url_for("dashboard.home"))

    novo = User(username=username, name=nome, email=email, is_admin=is_admin, password=generate_password_hash(senha))
    db.session.add(novo)
    db.session.commit()

    flash("Funcionário cadastrado com sucesso!", "success")
    return redirect(url_for("dashboard.home"))

@bp.route("/gerar-vpn", methods=["POST"])
@login_required
def gerar_vpn():
        try:
            print("Iniciando geração da VPN")
            info = gerar_vpn_para_usuario(current_user.username)
            print(f"ZIP gerado: {info['zip_path']}")
            return send_file(info["zip_path"],
                            as_attachment=True,
                            download_name=f"{info['identificador']}.zip",
                            mimetype='application/octet-stream')
        except Exception as e:
            print("Erro ao gerar VPN:", e)
            import traceback
            traceback.print_exc()
            flash("Erro ao gerar VPN: " + str(e), "danger")
            return redirect(url_for("dashboard.funcionario_dashboard"))

@bp.route("/funcionario")
@login_required
def funcionario_dashboard():
    from app.models import CertificadoVPN
    vpns = CertificadoVPN.query.filter_by(username=current_user.username).all()
    return render_template("funcionario.html", vpns=vpns)

@bp.route("/download-vpn/<ident>")
@login_required
def download_vpn(ident):
    from app.models import CertificadoVPN
    vpn = CertificadoVPN.query.filter_by(identificador=ident, username=current_user.username).first_or_404()
    return send_file(vpn.caminho_arquivo,
                     as_attachment=True,
                     download_name=f"{ident}.zip",
                     mimetype='application/octet-stream')

@bp.route("/remover-vpns", methods=["POST"])
@login_required
def remover_vpns():
    from app.models import CertificadoVPN
    idents = request.form.getlist("selecionadas")

    for ident in idents:
        vpn = CertificadoVPN.query.filter_by(identificador=ident, username=current_user.username).first()
        if vpn:
            #revoga o certificado via easy-rsa
            subprocess.run(["sudo", "./easyrsa", "revoke", ident], cwd="/usr/share/easy-rsa", check=True)
            subprocess.run(["sudo", "./easyrsa", "gen-crl"], cwd="/usr/share/easy-rsa", check=True)

            #remove o arquivo zip e registro
            if os.path.exists(vpn.caminho_arquivo):
                os.remove(vpn.caminho_arquivo)
            db.session.delete(vpn)

    db.session.commit()
    flash("Certificados removidos com sucesso.", "success")
    return redirect(url_for("dashboard.funcionario_dashboard"))


@bp.route("/funcionarios", methods=["GET"])
def lista_funcionarios():
    #impedir acesso de não-admins
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        flash("Acesso restrito ao administrador.", "danger")
        return redirect(url_for("dashboard.home"))

    filtro = request.args.get("filtro", "").strip()
    ordem = request.args.get("ordem", "username")
    direcao = request.args.get("direcao", "asc")

    query = User.query

    if filtro:
        query = query.filter(User.username.ilike(f"%{filtro}%"))

    if direcao == "desc":
        query = query.order_by(getattr(User, ordem).desc())
    else:
        query = query.order_by(getattr(User, ordem).asc())

    funcionarios = query.all()

    return render_template("lista_funcionarios.html", funcionarios=funcionarios, filtro=filtro, ordem=ordem, direcao=direcao)