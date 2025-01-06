from app import create_app
from flask import Blueprint, render_template, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import Flower, Category, Image
from app import db
import os
from flask import current_app
from werkzeug.utils import secure_filename

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@main_bp.route('/')
def index():
    flowers = Flower.query.all()
    return render_template('index.html', flowers=flowers)

@main_bp.route('/admin/add_flower', methods=['POST'])
@jwt_required()
def add_flower():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    data = request.form
    images = request.files.getlist('images')  # Получаем список загруженных файлов
    upload_folder = current_app.config['UPLOAD_FOLDER']  # Доступ через current_app

    # Создаем новый цветок
    new_flower = Flower(
        name=data.get('name'),
        description=data.get('description'),
        price=data.get('price'),
        category_id=data.get('category_id')
    )
    db.session.add(new_flower)
    db.session.flush()  # Получаем ID цветка до выполнения commit

    # Сохраняем изображения
    for image in images:
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            new_image = Image(url=f'/static/uploads/{filename}', flower_id=new_flower.id)
            db.session.add(new_image)

    db.session.commit()
    return redirect(url_for('main.admin'))

# Передаем категории в шаблон
@main_bp.route('/admin')
@jwt_required()
def admin():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    flowers = Flower.query.all()
    categories = Category.query.all()  # Получаем категории для выбора
    return render_template('admin.html', flowers=flowers, categories=categories)

@main_bp.route('/admin/categories', methods=['GET', 'POST'])
@jwt_required()
def manage_categories():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        category_name = request.form.get('name')
        if category_name:
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
        return redirect(url_for('main.manage_categories'))

    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@main_bp.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@jwt_required()
def delete_category(category_id):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for('main.manage_categories'))

@main_bp.route('/admin/categories/edit/<int:category_id>', methods=['POST'])
@jwt_required()
def edit_category(category_id):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    category = Category.query.get(category_id)
    if category:
        new_name = request.form.get('name')
        if new_name:
            category.name = new_name
            db.session.commit()
    return redirect(url_for('main.manage_categories'))
