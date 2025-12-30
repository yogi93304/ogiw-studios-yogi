from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # RBAC
    role = db.Column(db.String(20), nullable=False)  
    # nilai: "admin" | "staff"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Studio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    price_per_hour = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
