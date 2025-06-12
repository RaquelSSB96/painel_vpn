from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app():
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    login_manager.login_view = "auth.login" 
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes import dashboard
    app.register_blueprint(dashboard.bp)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    return app
