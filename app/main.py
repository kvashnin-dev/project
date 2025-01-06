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

@main_bp.route('/admin')
@jwt_required()
def admin():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    return render_template('admin.html')

@main_bp.route('/admin/flowers')
@jwt_required()
def manage_flowers():
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    flowers = Flower.query.all()
    categories = Category.query.all()
    return render_template('flowers.html', flowers=flowers, categories=categories)

@main_bp.route('/admin/flowers/delete/<int:flower_id>', methods=['POST'])
@jwt_required()
def delete_flower(flower_id):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    flower = Flower.query.get(flower_id)
    if flower:
        # Удаляем связанные изображения
        for image in flower.images:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(image.url))
            if os.path.exists(image_path):
                os.remove(image_path)  # Удаляем файл с диска
            db.session.delete(image)  # Удаляем запись из базы данных

        # Удаляем сам цветок
        db.session.delete(flower)
        db.session.commit()

    return redirect(url_for('main.manage_flowers'))

@main_bp.route('/admin/flowers/edit/<int:flower_id>', methods=['GET', 'POST'])
@jwt_required()
def edit_flower(flower_id):
    claims = get_jwt()
    if not claims.get("is_admin"):
        return redirect(url_for('auth.login'))

    flower = Flower.query.get(flower_id)
    if not flower:
        return redirect(url_for('main.manage_flowers'))

    if request.method == 'POST':
        # Обновляем данные цветка
        flower.name = request.form.get('name', flower.name)
        flower.description = request.form.get('description', flower.description)
        flower.price = request.form.get('price', flower.price)
        flower.category_id = request.form.get('category_id', flower.category_id)

        # Удаление изображений
        images_to_delete = request.form.getlist('delete_images')  # Получаем ID изображений для удаления
        for image_id in images_to_delete:
            image = Image.query.get(image_id)
            if image:
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.basename(image.url))
                if os.path.exists(image_path):
                    os.remove(image_path)  # Удаляем файл с диска
                db.session.delete(image)  # Удаляем запись из базы данных

        # Добавление новых изображений
        new_images = request.files.getlist('images')
        for image in new_images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)

                new_image = Image(url=f'/static/uploads/{filename}', flower_id=flower.id)
                db.session.add(new_image)

        db.session.commit()
        return redirect(url_for('main.manage_flowers'))

    categories = Category.query.all()
    return render_template('edit_flower.html', flower=flower, categories=categories)

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
    return redirect(url_for('main.manage_flowers'))

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
