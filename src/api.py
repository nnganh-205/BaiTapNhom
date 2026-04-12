from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Cart, CartItem, Order, Product, ProductVariant, User

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


def _user_payload(user):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role,
    }


def _require_json(fields):
    data = request.get_json(silent=True) or {}
    missing = [field for field in fields if not str(data.get(field, "")).strip()]
    if missing:
        return None, (
            jsonify({"message": "Thiếu dữ liệu bắt buộc.", "missing_fields": missing}),
            400,
        )
    return data, None


def _admin_guard():
    if not current_user.is_authenticated:
        return jsonify({"message": "Unauthorized"}), 401
    if current_user.role != "admin":
        return jsonify({"message": "Forbidden"}), 403
    return None


def _get_or_create_cart(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if cart:
        return cart
    cart = Cart(user_id=user_id)
    db.session.add(cart)
    db.session.commit()
    return cart


def _serialize_cart(cart):
    items = []
    total_amount = 0.0
    total_quantity = 0

    for item in cart.items:
        product = Product.query.get(item.product_id)
        if not product:
            continue

        variant = None
        if item.variant_id:
            variant = ProductVariant.query.get(item.variant_id)
        if not variant:
            variant = ProductVariant.query.filter_by(product_id=product.id).order_by(ProductVariant.price.asc()).first()

        unit_price = float(variant.price) if variant else 0.0
        line_total = unit_price * item.quantity
        total_amount += line_total
        total_quantity += item.quantity

        items.append(
            {
                "id": item.id,
                "product_id": product.id,
                "product_name": product.name,
                "image_url": product.image_url,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "line_total": line_total,
            }
        )

    return {
        "cart_id": cart.id,
        "items": items,
        "total_amount": total_amount,
        "total_quantity": total_quantity,
    }


@api_bp.post("/auth/login")
def api_login():
    data, error = _require_json(["username", "password"])
    if error:
        return error

    username = data["username"].strip()
    password = data["password"]
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Sai tên đăng nhập hoặc mật khẩu."}), 401

    login_user(user)
    return jsonify({"message": "Đăng nhập thành công.", "user": _user_payload(user)}), 200


@api_bp.post("/auth/register")
def api_register():
    data, error = _require_json(["username", "full_name", "email", "password"])
    if error:
        return error

    username = data["username"].strip()
    full_name = data["full_name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Tên đăng nhập đã tồn tại."}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã được sử dụng."}), 409

    user = User(username=username, full_name=full_name, email=email, role="customer")
    user.set_password(password)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Không thể tạo tài khoản."}), 500

    return jsonify({"message": "Đăng ký thành công.", "user": _user_payload(user)}), 201


@api_bp.post("/auth/logout")
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Đăng xuất thành công."}), 200


@api_bp.get("/auth/me")
@login_required
def api_me():
    return jsonify({"user": _user_payload(current_user)}), 200


@api_bp.get("/admin/overview")
def api_admin_overview():
    guard_error = _admin_guard()
    if guard_error:
        return guard_error

    return jsonify(
        {
            "users": User.query.count(),
            "products": Product.query.count(),
            "orders": Order.query.count(),
        }
    ), 200


@api_bp.get("/cart")
@login_required
def api_get_cart():
    cart = _get_or_create_cart(current_user.id)
    return jsonify(_serialize_cart(cart)), 200


@api_bp.post("/cart/items")
@login_required
def api_add_cart_item():
    data, error = _require_json(["product_id", "quantity"])
    if error:
        return error

    try:
        product_id = int(data["product_id"])
        quantity = int(data["quantity"])
    except (TypeError, ValueError):
        return jsonify({"message": "Dữ liệu sản phẩm không hợp lệ."}), 400

    if quantity < 1:
        return jsonify({"message": "Số lượng phải lớn hơn 0."}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Không tìm thấy sản phẩm."}), 404

    cart = _get_or_create_cart(current_user.id)
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        variant = ProductVariant.query.filter_by(product_id=product_id).order_by(ProductVariant.price.asc()).first()
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            variant_id=variant.id if variant else None,
            quantity=quantity,
        )
        db.session.add(item)

    db.session.commit()
    return jsonify(_serialize_cart(cart)), 201


@api_bp.patch("/cart/items/<int:item_id>")
@login_required
def api_update_cart_item(item_id):
    data, error = _require_json(["quantity"])
    if error:
        return error

    try:
        quantity = int(data["quantity"])
    except (TypeError, ValueError):
        return jsonify({"message": "Số lượng không hợp lệ."}), 400

    cart = _get_or_create_cart(current_user.id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({"message": "Không tìm thấy mục giỏ hàng."}), 404

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity

    db.session.commit()
    return jsonify(_serialize_cart(cart)), 200


@api_bp.delete("/cart/items/<int:item_id>")
@login_required
def api_delete_cart_item(item_id):
    cart = _get_or_create_cart(current_user.id)
    item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first()
    if not item:
        return jsonify({"message": "Không tìm thấy mục giỏ hàng."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify(_serialize_cart(cart)), 200


