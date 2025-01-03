from flask_jwt_extended import JWTManager           
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')  # Замените на ваш ключ

    db.init_app(app)
    migrate.init_app(app, db)

    jwt = JWTManager(app)

    from .auth_routes import auth_bp
    app.register_blueprint(auth_bp)

    return app
