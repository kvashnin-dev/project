from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False  # Установите True, если используете HTTPS
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)  # Срок действия токена - 1 день

    db.init_app(app)
    migrate.init_app(app, db)

    jwt = JWTManager(app)

    # Регистрация блюпринтов
    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    # Регистрация маршрутов витрины и админки
    from .main import main_bp
    app.register_blueprint(main_bp)

    return app
