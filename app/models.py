from . import db

class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    images = db.relationship('Image', backref='flower', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    flowers = db.relationship('Flower', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flower.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
