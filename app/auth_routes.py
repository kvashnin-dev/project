from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity ,decode_token, get_jwt
from .models import db, User, Flower

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Проверяем, есть ли токен в куках
    token = request.cookies.get('access_token_cookie')
    
    if token:
        try:
            # Декодируем токен и проверяем срок действия
            decoded_token = decode_token(token)
            # Проверяем, что identity токена соответствует ожидаемому формату
            username = decoded_token.get('sub')  # sub — это идентификатор пользователя (username)
            if username:
                user = User.query.filter_by(username=username).first()
                if user:  # Убедимся, что пользователь существует в базе данных
                    # Перенаправляем в админку или на главную страницу
                    return redirect('/admin' if user.is_admin else '/')
        except Exception as e:
            # Если токен недействителен или истек, продолжаем с логином
            pass
    
    # Если токен недействителен или отсутствует, продолжаем обычный процесс логина
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return render_template('login.html', error="Username and password are required")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return render_template('login.html', error="Invalid username or password")

    access_token = create_access_token(
        identity=username,  # Передаем username как строку
        additional_claims={"is_admin": user.is_admin}  # Дополнительные данные
    )
    response = make_response(redirect('/admin' if user.is_admin else '/'))
    response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False)

    return response

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    # Удаляем токен, если он есть
    response = make_response(redirect('/auth/login'))
    response.delete_cookie('access_token_cookie')  # Удаляем куку с токеном
    return response
