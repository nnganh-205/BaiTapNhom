from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse

from . import db
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _home_by_role(role):
    if role == "admin":
        return "admin.admin_index"
    return "user.user_index"


def _is_safe_next(next_url):
    if not next_url:
        return False
    parsed = urlparse(next_url)
    return parsed.scheme == "" and parsed.netloc == ""


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(_home_by_role(current_user.role)))

    next_page = request.args.get("next")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        next_page = request.form.get("next", "")

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash("Sai tên đăng nhập hoặc mật khẩu.", "error")
            return render_template("auth/login.html", mode="login")

        login_user(user)
        if _is_safe_next(next_page):
            return redirect(next_page)
        return redirect(url_for(_home_by_role(user.role)))

    return render_template("auth/login.html", mode="login", next_page=next_page)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(_home_by_role(current_user.role)))

    next_page = request.args.get("next")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not full_name or not email or not password:
            flash("Vui lòng nhập đầy đủ thông tin.", "error")
            return render_template("auth/login.html", mode="register", next_page=next_page)

        if User.query.filter_by(username=username).first():
            flash("Tên đăng nhập đã tồn tại.", "error")
            return render_template("auth/login.html", mode="register", next_page=next_page)

        if User.query.filter_by(email=email).first():
            flash("Email đã được sử dụng.", "error")
            return render_template("auth/login.html", mode="register", next_page=next_page)

        is_first_user = User.query.first() is None
        role = "admin" if is_first_user else "customer"

        user = User(username=username, full_name=full_name, email=email, role=role)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Không thể tạo tài khoản. Vui lòng thử lại.", "error")
            return render_template("auth/login.html", mode="register", next_page=next_page)

        flash("Đăng ký thành công. Mời bạn đăng nhập.", "success")
        if next_page:
            return redirect(url_for("auth.login", next=next_page))
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html", mode="register", next_page=next_page)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.user_index"))




