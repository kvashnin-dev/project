from app import create_app
from flask import Blueprint, render_template, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import Flower
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    flowers = Flower.query.all()
    return render_template('index.html', flowers=flowers)

@main_bp.route('/admin')
@jwt_required()
def admin():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    flowers = Flower.query.all()
    return render_template('admin.html', flowers=flowers)

@main_bp.route('/admin/add_flower', methods=['POST'])
@jwt_required()
def add_flower():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    data = request.form
    new_flower = Flower(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        category_id=data.get('category_id')
    )
    db.session.add(new_flower)
    db.session.commit()

    return redirect(url_for('main.admin'))

# Добавляем проверку на запуск из командной строки
if __name__ == "__main__":
    app = create_app()  # Теперь вызываем функцию create_app для создания приложения
    app.run(host="0.0.0.0", port=5001)
