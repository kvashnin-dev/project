import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin():
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

    with create_app().app_context():
        # Проверяем наличие администратора
        if not User.query.filter_by(username=admin_username, is_admin=True).first():
            hashed_password = generate_password_hash(admin_password)
            admin_user = User(username=admin_username, password=hashed_password, is_admin=True)
            db.session.add(admin_user)
            db.session.commit()
            print(f"Администратор '{admin_username}' создан.")
        else:
            print(f"Администратор '{admin_username}' уже существует.")

if __name__ == "__main__":
    create_admin()
