import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def _ensure_default_admin(user_model):
    admin_user = user_model.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = user_model(
            username='admin',
            full_name='Quản trị hệ thống',
            email='admin@invenstory.local',
            role='admin',
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        return

    has_changes = False
    if admin_user.role != 'admin':
        admin_user.role = 'admin'
        has_changes = True

    # Keep admin/admin123 consistent for demo and grading requirements.
    if not admin_user.check_password('admin123'):
        admin_user.set_password('admin123')
        has_changes = True

    if has_changes:
        db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'nhom2'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
    app.config['VNPAY_TMN_CODE'] = os.getenv('VNPAY_TMN_CODE', '2Q317UM9')
    app.config['VNPAY_HASH_SECRET'] = os.getenv('VNPAY_HASH_SECRET', 'FUUALKGIDFW1IFSF73X3TP4ZO6H6AWJ2')
    app.config['VNPAY_PAYMENT_URL'] = os.getenv('VNPAY_PAYMENT_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
    app.config['VNPAY_RETURN_URL'] = os.getenv('VNPAY_RETURN_URL', 'http://127.0.0.1:5050/payment/vnpay/callback')
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User,Category,Product,ProductVariant,Cart,CartItem,Order,OrderItem,Payment,Review

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        if not os.path.exists('instance/data.db'):
            db.create_all()
        _ensure_default_admin(User)
    from .admin import admin_bp
    from .auth import auth_bp
    from .api import api_bp
    from .user import user_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    return app