from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    # Relationships
    books = db.relationship('Book', backref='user', lazy=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)

    title = db.Column(db.String(100), unique=False)
    author = db.Column(db.String(100), unique=False)
    date_published = db.Column(db.DateTime())
    uuid = db.Column(db.String(32), unique=True)
    publisher_name = db.Column(db.String(100), unique=False)
    s3_name = db.Column(db.String(100), unique=False)
    s3_url = db.Column(db.String(100), unique=False)
