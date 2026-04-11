import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'nhom2'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    db.init_app(app)
    from .models import User,Category,Product,ProductVariant,Cart,CartItem,Order,OrderItem,Payment,Review
    if not os.path.exists('instance/data.db'):
      with app.app_context():
        db.create_all()
    from .admin import admin_bp
    app.register_blueprint(admin_bp)
    return app