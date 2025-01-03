from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, decode_token
from .models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    token = request.cookies.get('access_token_cookie')

    if token:
        try:
            decoded_token = decode_token(token)
            username = decoded_token.get('sub')
            user = User.query.filter_by(username=username).first()
            if user:
                return redirect(url_for('main.admin' if user.is_admin else 'main.index'))
        except Exception:
            pass

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
        identity=username,
        additional_claims={"is_admin": user.is_admin}
    )
    response = make_response(redirect(url_for('main.admin' if user.is_admin else 'main.index')))
    response.set_cookie('access_token_cookie', access_token, httponly=True, secure=True)

    return response

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    response = make_response(redirect(url_for('auth.login')))
    response.delete_cookie('access_token_cookie')
    return response
