import os
import subprocess
import zipfile
import secrets
import string
import getpass
from datetime import datetime, timedelta

VPN_BASE_PATH = "/home/userlinux/vpn_clientes"
ZIP_EXPORT_PATH = "/home/userlinux/vpns"
EASY_RSA_PATH = "/usr/share/easy-rsa"

def gerar_identificador():
    while True:
        ident = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        if not os.path.exists(os.path.join(VPN_BASE_PATH, ident)):
            return ident

def gerar_vpn_para_usuario(username):
    print("🔧 VPN chamada")
    ident = gerar_identificador()
    base_dir = os.path.join(VPN_BASE_PATH, ident)
    os.makedirs(base_dir, exist_ok=True)

    #evita prompt de Common Name
    env = os.environ.copy()
    env["EASYRSA_REQ_CN"] = ident
    env["EASYRSA_BATCH"] = "1"

    #gera request
    subprocess.run(
        ["sudo", "./easyrsa", "gen-req", ident, "nopass"],
        cwd=EASY_RSA_PATH,
        check=True,
        env=env
    )

    #assina automaticamente
    subprocess.run(
        ["sudo", "./easyrsa", "sign-req", "client", ident],
        cwd=EASY_RSA_PATH,
        input=b"yes\n",
        check=True,
        env=env
    )

    #copia os arquivos
    arquivos = {
        f"{EASY_RSA_PATH}/pki/issued/{ident}.crt": f"{base_dir}/{ident}.crt",
        f"{EASY_RSA_PATH}/pki/private/{ident}.key": f"{base_dir}/{ident}.key",
        f"{EASY_RSA_PATH}/pki/ca.crt": f"{base_dir}/ca.crt",
        f"{EASY_RSA_PATH}/pki/dh.pem": f"{base_dir}/dh.pem"
    }

    for origem, destino in arquivos.items():
        subprocess.run(["sudo", "cp", origem, destino])
        subprocess.run(["sudo", "chown", f"{username}:{username}", destino])
        subprocess.run(["sudo", "chmod", "644", destino])

    #gera o .ovpn
    with open(os.path.join(base_dir, f"{ident}.ovpn"), "w") as f:
        f.write(f"""client
dev tun
proto udp
remote 192.168.0.16 1194
ca ca.crt
cert {ident}.crt
key {ident}.key
tls-client
resolv-retry infinite
nobind
persist-key
persist-tun
""")

    #compacta os arquivos
    os.makedirs(ZIP_EXPORT_PATH, exist_ok=True)
    zip_path = os.path.join(ZIP_EXPORT_PATH, f"{ident}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in os.listdir(base_dir):
            zipf.write(os.path.join(base_dir, file), arcname=file)

    #retorna dados
    return {
        "identificador": ident,
        "zip_path": zip_path,
        "data_criacao": datetime.now(),
        "expira_em": datetime.now() + timedelta(days=7)
    }
