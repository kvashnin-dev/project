from app import create_app  # Импортируем функцию создания приложения
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import Flower
from app import db

# Создаем Blueprint для основного приложения
main_bp = Blueprint('main', __name__)

# Витрина цветов
@main_bp.route('/')
def index():
    flowers = Flower.query.all()  # Получаем все цветы из базы данных
    return render_template('index.html', flowers=flowers)

@main_bp.route('/admin')
@jwt_required()  # Проверяет токен из access_token_cookie
def admin():
    current_user = get_jwt_identity()  # Возвращает строку identity
    
    # Проверяем дополнительные claims
    claims = get_jwt()
    is_admin = claims.get("is_admin", False)

    if not is_admin:
        return redirect(url_for('auth.login'))

    flowers = Flower.query.all()
    return render_template('admin.html', flowers=flowers)


# Для защищенных маршрутов (например, создание и редактирование цветов)
@main_bp.route('/admin/add_flower', methods=['POST'])
@jwt_required()
def add_flower():
    current_user = get_jwt_identity()
    if not current_user["is_admin"]:
        return jsonify({"message": "Access denied"}), 403

    data = request.json
    new_flower = Flower(name=data["name"], description=data["description"], price=data["price"], category_id=data["category_id"])
    db.session.add(new_flower)
    db.session.commit()

    return jsonify({"message": "Flower added successfully!"}), 201

# Добавляем проверку на запуск из командной строки
if __name__ == "__main__":
    app = create_app()  # Теперь вызываем функцию create_app для создания приложения
    app.run(host="0.0.0.0", port=5001)
