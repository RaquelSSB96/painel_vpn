import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "chave-secreta-segura"
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'topsredes@gmail.com'
    MAIL_PASSWORD = 'oztrovrditlrpqta'
    MAIL_DEFAULT_SENDER = MAIL_USERNAME
    MAIL_USE_SSL = False


