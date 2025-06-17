# Painel VPN com Flask
Este projeto é um painel web feito com Flask que permite que **usuários gerem e baixem seus próprios arquivos de configuração de VPN (.ovpn)**, integrando-se diretamente com o Easy-RSA e o OpenVPN instalados na máquina.

# Objetivo
Facilitar o processo de geração e gerenciamento de certificados de VPN para usuários finais via interface web, sem precisar interagir diretamente com o terminal.

# Funcionalidades
- Login de usuários;
- Geração automática de arquivos `.ovpn` com certificado e chave;
- Download em `.zip` de todas as credenciais necessárias;
- Interface diferenciada para administradores e usuários.

# Pré-requisitos
Antes de clonar o projeto, você precisa garantir que seu ambiente esteja pronto:

# 1. **Sistema Operacional**
- Recomendado: Debian (Linux)

# 2. **Instale os pacotes necessários**
```bash
sudo apt update
sudo apt install openvpn easy-rsa python3 python3-pip git -y
```

# 3. **Clone o repositório**
```bash
git clone https://github.com/RaquelSSB96/painel_vpn.git
cd painel_vpn
```

# 4. **Crie e ative um ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate
```

# 5. **Instale as dependências do Python**
```bash
pip install -r requirements.txt
```

# 6. **Configure o Easy-RSA**
```bash
cd /usr/share/easy-rsa
sudo ./easyrsa init-pki
sudo ./easyrsa build-ca nopass < /dev/null
```
**Se você já possui uma CA configurada, pule a última linha.**

# Executando o painel
Volte à pasta do projeto e execute:

```bash
cd ~/vpn-painel
source venv/bin/activate
python run.py
```

Depois acesse no navegador:  
`http://127.0.0.1:5000`


# Estrutura de pastas utilizada
O projeto espera encontrar (e cria automaticamente) as seguintes pastas com permissões adequadas:

- `/home/seu_usuário/vpn_clientes` → onde os arquivos de VPN individuais são armazenados
- `/home/seu_usuário/vpns` → onde os arquivos `.zip` são gerados

**Esses caminhos estão fixos no código. Se quiser usar outros diretórios ou rodar em outro usuário, você deverá alterar diretamente os caminhos em** `vpn_generator.py`.

# Permissões
Certifique-se de dar permissão total às pastas esperadas:
```bash
sudo mkdir -p /home/seu_usuário/vpn_clientes /home/seu_usuário/vpns
sudo chown -R $USER:$USER /home/seu_usuário/vpn_clientes /home/seu_usuário/vpns
```

# Observações importantes
- O Easy-RSA deve estar funcional e com a CA já criada;
- O projeto roda localmente e exige permissões de `sudo` para assinar os certificados;
- A senha do sudo não é solicitada no terminal se o script for corretamente configurado;
- O campo `commonName` (CN) é atribuído automaticamente com base em um identificador aleatório.
