from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, decode_token
from datetime import timedelta, datetime
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # Ограничение на размер файла (2 МБ)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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

    from .main import main_bp
    app.register_blueprint(main_bp)

    # Проверка токена
    def is_token_valid():
        token = request.cookies.get('access_token_cookie')
        if not token:
            return False
        try:
            decoded_token = decode_token(token)
            if decoded_token['exp'] > datetime.utcnow().timestamp():
                return True
        except Exception:
            pass
        return False

    # Контекстный процессор
    @app.context_processor
    def inject_token_status():
        return {'token_valid': is_token_valid()}

    return app
