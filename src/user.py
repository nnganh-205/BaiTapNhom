from datetime import datetime

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, or_

from . import db
from .models import Cart, CartItem, Category, Order, OrderItem, Payment, Product, ProductVariant, Review
from .promotions import evaluate_checkout_pricing, get_checkout_promo_options, is_lucky_hour_now
from .vnpay import VNPayGateway

user_bp = Blueprint("user", __name__)
SIZE_LABELS = {"S": "Vừa", "L": "To"}


def _variant_sale_price(variant: ProductVariant | None) -> float:
    if not variant:
        return 0.0
    base_price = float(variant.price or 0)
    percent = max(0.0, min(100.0, float(variant.discount_percent or 0)))
    return round(base_price * (1 - percent / 100.0), 2)


def _get_user_cart_items(user_id):
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return [], 0

    items = []
    subtotal = 0.0
    for item in cart.items:
        product = Product.query.get(item.product_id)
        if not product:
            continue

        variant = ProductVariant.query.get(item.variant_id) if item.variant_id else None
        if not variant:
            variant = ProductVariant.query.filter_by(product_id=product.id).order_by(ProductVariant.price.asc()).first()

        unit_price = _variant_sale_price(variant)
        original_price = float(variant.price) if variant else 0.0
        discount_percent = float(variant.discount_percent or 0) if variant else 0.0
        size_name = (item.size_name or "S").upper()
        size_extra = float(item.size_extra or 0)
        unit_price += size_extra
        line_total = unit_price * item.quantity
        subtotal += line_total

        items.append(
            {
                "id": item.id,
                "product_id": product.id,
                "variant_id": variant.id if variant else None,
                "name": product.name,
                "image_url": product.image_url,
                "quantity": item.quantity,
                "price": unit_price,
                "original_price": original_price,
                "discount_percent": discount_percent,
                "size_name": size_name,
                "size_label": SIZE_LABELS.get(size_name, size_name),
                "size_extra": size_extra,
                "line_total": line_total,
                "stock": int(variant.stock or 0) if variant else 0,
            }
        )

    return items, subtotal


def _get_order_items(order_id):
    rows = (
        db.session.query(OrderItem, Product)
        .join(Product, Product.id == OrderItem.product_id)
        .filter(OrderItem.order_id == order_id)
        .all()
    )
    items = []
    for order_item, product in rows:
        line_total = float(order_item.price_at_purchase) * order_item.quantity
        items.append(
            {
                "product_name": product.name,
                "quantity": order_item.quantity,
                "unit_price": float(order_item.price_at_purchase),
                "size_name": (order_item.size_name or "S").upper(),
                "size_label": SIZE_LABELS.get((order_item.size_name or "S").upper(), (order_item.size_name or "S").upper()),
                "size_extra": float(order_item.size_extra or 0),
                "line_total": line_total,
            }
        )
    return items


def _refresh_product_availability(product_id):
    product = Product.query.get(product_id)
    if not product:
        return
    product.is_available = any((variant.stock or 0) > 0 for variant in product.variants)


def _find_variant_for_cart_item(product_id, variant_id):
    if variant_id:
        variant = ProductVariant.query.get(variant_id)
        if variant:
            return variant
    return ProductVariant.query.filter_by(product_id=product_id).order_by(ProductVariant.price.asc()).first()


def _get_lucky_showcase_products(limit: int = 10):
    fallback_image = "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=1200&auto=format&fit=crop"
    products = Product.query.order_by(Product.created_at.desc()).all()
    candidates = []
    for product in products:
        if not product.is_available:
            continue
        variants = product.variants or []
        total_stock = sum(int(v.stock or 0) for v in variants)
        if total_stock <= 0:
            continue
        min_price = min((float(v.price) for v in variants), default=0.0)
        if min_price <= 0:
            continue
        candidates.append(
            {
                "id": product.id,
                "name": product.name,
                "image_url": product.image_url or fallback_image,
                "price": min_price,
                "discounted_price": min_price * 0.85,
                "stock": total_stock,
            }
        )

    candidates.sort(key=lambda item: item["stock"], reverse=True)
    return candidates[:limit]


def _build_discount_progress(subtotal: float, promo_code: str, promo_options):
    goals = [
        {"label": "Miễn phí ship", "threshold": 90000, "code": "FREESHIP90"},
        {"label": "Giảm 30.000đ", "threshold": 130000, "code": "SAVE30_130"},
        {"label": "Khung giờ vàng", "threshold": 150000, "code": "LUCKY15"},
    ]

    eligible_codes = {item.get("code") for item in promo_options if item.get("eligible")}
    progress = []
    for goal in goals:
        remaining = max(0, int(goal["threshold"] - subtotal))
        is_unlocked = remaining <= 0
        is_confirmed = promo_code == goal["code"] or (is_unlocked and goal["code"] == "FREESHIP90")
        progress.append(
            {
                "label": goal["label"],
                "threshold": goal["threshold"],
                "remaining": remaining,
                "is_unlocked": is_unlocked,
                "is_confirmed": is_confirmed or (goal["code"] in eligible_codes and goal["code"] == promo_code),
                "code": goal["code"],
            }
        )
    return progress


@user_bp.route("/")
def user_index():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "all").strip()
    sort = request.args.get("sort", "newest").strip()

    query = Product.query

    if search_query:
        keyword = f"%{search_query}%"
        query = query.filter(or_(Product.name.ilike(keyword), Product.description.ilike(keyword)))

    selected_category_id = None
    if category_filter != "all":
        try:
            selected_category_id = int(category_filter)
            query = query.filter(Product.category_id == selected_category_id)
        except ValueError:
            category_filter = "all"

    if sort in {"price-low", "price-high"}:
        price_expr = func.coalesce(func.min(ProductVariant.price), 0)
        query = query.outerjoin(ProductVariant).group_by(Product.id)
        if sort == "price-low":
            query = query.order_by(price_expr.asc(), Product.created_at.desc())
        else:
            query = query.order_by(price_expr.desc(), Product.created_at.desc())
    else:
        sort = "newest"
        query = query.order_by(Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=9, error_out=False)
    products = pagination.items

    fallback_image = "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=1200&auto=format&fit=crop"
    product_cards = []
    for product in products:
        variants = product.variants or []
        best_variant = min(variants, key=_variant_sale_price) if variants else None
        min_price = _variant_sale_price(best_variant)
        original_price = float(best_variant.price or 0) if best_variant else 0.0
        discount_percent = float(best_variant.discount_percent or 0) if best_variant else 0.0
        total_stock = sum((v.stock or 0) for v in variants)
        product_cards.append(
            {
                "id": product.id,
                "name": product.name,
                "description": product.description or "Hương vị thơm ngon, phù hợp cho mọi bữa ăn.",
                "image_url": product.image_url or fallback_image,
                "price": min_price,
                "original_price": original_price,
                "discount_percent": discount_percent,
                "is_available": bool(product.is_available and total_stock > 0),
                "category_id": product.category_id,
            }
        )

    top_rows = (
        Product.query.join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status != "cancelled")
        .with_entities(
            Product.id,
            func.sum(OrderItem.quantity).label("total_ordered"),
        )
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(6)
        .all()
    )
    top_ids = [row.id for row in top_rows]
    ordered_count = {row.id: int(row.total_ordered or 0) for row in top_rows}

    top_products = []
    if top_ids:
        top_product_map = {
            p.id: p
            for p in Product.query.filter(Product.id.in_(top_ids)).all()
        }
        for product_id in top_ids:
            product = top_product_map.get(product_id)
            if not product:
                continue
            variants = product.variants or []
            best_variant = min(variants, key=_variant_sale_price) if variants else None
            min_price = _variant_sale_price(best_variant)
            top_products.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "total_ordered": ordered_count.get(product.id, 0),
                    "price": min_price,
                }
            )

    categories = Category.query.order_by(Category.name.asc()).all()

    return render_template(
        "user/index.html",
        products=product_cards,
        categories=categories,
        top_product_ids=set(top_ids),
        top_products=top_products,
        current_page=pagination.page,
        total_pages=max(pagination.pages, 1),
        current_search=search_query,
        current_category=str(category_filter),
        current_sort=sort,
    )


@user_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart_items, subtotal = _get_user_cart_items(current_user.id)
    if not cart_items:
        flash("Giỏ hàng đang trống.", "error")
        return redirect(url_for("user.user_index"))

    lucky_hour_active = is_lucky_hour_now()
    lucky_products = _get_lucky_showcase_products(limit=10) if lucky_hour_active else []

    # Only items displayed in Lucky Hour showcase should receive Lucky15 discount.
    lucky_product_ids = {int(item.get("id")) for item in lucky_products}
    for item in cart_items:
        item["is_lucky_item"] = bool(lucky_hour_active and int(item.get("product_id") or 0) in lucky_product_ids)

    promo_code = ""
    if request.method == "POST":
        promo_code = (request.form.get("promo_code", "") or "").strip().upper()
        if not promo_code:
            selected_codes = request.form.getlist("promo_codes")
            promo_code = (selected_codes[0] if selected_codes else "").strip().upper()
    else:
        promo_code = (request.args.get("promo_code", "") or "").strip().upper()
    promo_options = get_checkout_promo_options(cart_items=cart_items, subtotal=subtotal)

    # Auto-select lucky promo when user is in lucky hour and has not chosen another code.
    if lucky_hour_active and not promo_code:
        lucky_option = next((opt for opt in promo_options if opt.get("code") == "LUCKY15"), None)
        if lucky_option and lucky_option.get("eligible"):
            promo_code = "LUCKY15"

    pricing = evaluate_checkout_pricing(cart_items=cart_items, subtotal=subtotal, promo_code=promo_code)
    shipping_fee = pricing["shipping_fee"]
    shipping_discount = pricing["shipping_discount"]
    promotion_discount = pricing["promotion_discount"]
    applied_promotions = pricing["applied_promotions"]
    grand_total = pricing["grand_total"]
    discount_progress = _build_discount_progress(subtotal=subtotal, promo_code=promo_code, promo_options=promo_options)

    def render_checkout_page():
        return render_template(
            "user/checkout.html",
            cart_items=cart_items,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            shipping_discount=shipping_discount,
            promotion_discount=promotion_discount,
            applied_promotions=applied_promotions,
            promo_code=promo_code,
            promo_options=promo_options,
            grand_total=grand_total,
            lucky_hour_active=lucky_hour_active,
            lucky_products=lucky_products,
            discount_progress=discount_progress,
        )

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        note = request.form.get("note", "").strip()
        payment_method = request.form.get("payment_method", "cod").strip()

        if not full_name or not phone or not address:
            flash("Vui lòng nhập đầy đủ thông tin thanh toán.", "error")
            return render_checkout_page()

        if payment_method not in {"cod", "vnpay"}:
            flash("Phương thức thanh toán không hợp lệ.", "error")
            return render_checkout_page()

        pricing = evaluate_checkout_pricing(cart_items=cart_items, subtotal=subtotal, promo_code=promo_code)
        shipping_fee = pricing["shipping_fee"]
        shipping_discount = pricing["shipping_discount"]
        promotion_discount = pricing["promotion_discount"]
        applied_promotions = pricing["applied_promotions"]
        grand_total = pricing["grand_total"]
        if pricing["messages"]:
            for msg in pricing["messages"]:
                flash(msg, "error")
            return render_checkout_page()

        stock_errors = []
        resolved_variants = {}
        for item in cart_items:
            variant = _find_variant_for_cart_item(item["product_id"], item.get("variant_id"))
            if not variant:
                stock_errors.append(f"{item['name']} chưa có biến thể giá.")
                continue
            resolved_variants[item["id"]] = variant
            available_stock = int(variant.stock or 0)
            if available_stock < int(item["quantity"]):
                stock_errors.append(f"{item['name']} chỉ còn {available_stock} sản phẩm.")

        if stock_errors:
            flash("Không thể đặt hàng: " + " ".join(stock_errors), "error")
            return render_checkout_page()

        order_code = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        order = Order(
            order_code=order_code,
            user_id=current_user.id,
            total_price=grand_total,
            status="pending",
            shipping_address=address,
            note=(
                note
                + (f"\n[Khuyen mai ap dung: {', '.join(applied_promotions)}]" if applied_promotions else "")
                + (f"\n[Ma giam gia: {promo_code}]" if promo_code else "")
            ).strip(),
        )
        db.session.add(order)
        db.session.flush()

        txn_ref = f"{order.id}{datetime.now().strftime('%H%M%S')}"
        payment = Payment(
            order_id=order.id,
            payment_method=payment_method,
            amount=grand_total,
            payment_status="pending",
            vnp_txn_ref=txn_ref if payment_method == "vnpay" else None,
        )
        db.session.add(payment)

        for item in cart_items:
            variant = resolved_variants.get(item["id"])
            if not variant:
                continue
            db.session.add(
                OrderItem(
                    order_id=order.id,
                    product_id=item["product_id"],
                    variant_id=variant.id,
                    quantity=item["quantity"],
                    price_at_purchase=item["price"],
                    size_name=item.get("size_name") or "S",
                    size_extra=item.get("size_extra") or 0,
                )
            )
            variant.stock = int(variant.stock or 0) - int(item["quantity"])
            _refresh_product_availability(item["product_id"])

        if payment_method == "vnpay":
            db.session.commit()
            gateway = VNPayGateway(current_app)
            payment_url = gateway.create_payment_url(
                txn_ref=txn_ref,
                amount=grand_total,
                order_info=f"Thanh toan don hang {order_code}",
                ip_addr=request.remote_addr or "127.0.0.1",
                return_url=url_for("user.vnpay_callback", _external=True),
            )
            return redirect(payment_url)

        payment.payment_status = "pending"
        order.status = "pending"
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()

        db.session.commit()
        flash("Đặt hàng thành công! Đơn hàng của bạn đang được xử lý.", "success")
        return redirect(url_for("user.user_index"))

    return render_checkout_page()


@user_bp.route("/profile")
@login_required
def profile():
    return render_template("user/profile.html")


@user_bp.route("/orders")
@login_required
def my_orders():
    placed_orders = (
        Order.query.filter_by(user_id=current_user.id, status="pending")
        .order_by(Order.created_at.desc())
        .all()
    )
    received_orders = (
        Order.query.filter_by(user_id=current_user.id, status="completed")
        .order_by(Order.created_at.desc())
        .all()
    )
    active_tab = request.args.get("tab", "placed")
    if active_tab not in {"placed", "received"}:
        active_tab = "placed"

    return render_template(
        "user/orders.html",
        placed_orders=placed_orders,
        received_orders=received_orders,
        active_tab=active_tab,
    )


@user_bp.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Không tìm thấy đơn hàng.", "error")
        return redirect(url_for("user.my_orders"))

    items = _get_order_items(order.id)
    review = Review.query.filter_by(order_id=order.id, user_id=current_user.id).first()
    return render_template("user/order_detail.html", order=order, items=items, review=review)


@user_bp.route("/orders/<int:order_id>/confirm", methods=["POST"])
@login_required
def confirm_received(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Không tìm thấy đơn hàng.", "error")
        return redirect(url_for("user.my_orders"))

    if order.status != "pending":
        flash("Đơn hàng đã được xác nhận trước đó.", "error")
        return redirect(url_for("user.order_detail", order_id=order.id))

    order.status = "completed"
    if order.payment and order.payment.payment_method == "cod" and order.payment.payment_status == "pending":
        order.payment.payment_status = "completed"
    db.session.commit()
    flash("Bạn đã xác nhận nhận hàng thành công.", "success")
    return redirect(url_for("user.order_detail", order_id=order.id))


@user_bp.route("/orders/<int:order_id>/review", methods=["POST"])
@login_required
def submit_review(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if not order:
        flash("Không tìm thấy đơn hàng.", "error")
        return redirect(url_for("user.my_orders"))

    if order.status != "completed":
        flash("Chỉ đánh giá sau khi đã nhận hàng.", "error")
        return redirect(url_for("user.order_detail", order_id=order.id))

    if Review.query.filter_by(order_id=order.id, user_id=current_user.id).first():
        flash("Đơn hàng này đã được đánh giá.", "error")
        return redirect(url_for("user.order_detail", order_id=order.id))

    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()
    if not rating or rating < 1 or rating > 5:
        flash("Vui lòng chọn số sao từ 1 đến 5.", "error")
        return redirect(url_for("user.order_detail", order_id=order.id))

    db.session.add(Review(user_id=current_user.id, order_id=order.id, rating=rating, comment=comment))
    db.session.commit()
    flash("Cảm ơn bạn đã đánh giá món ăn.", "success")
    return redirect(url_for("user.order_detail", order_id=order.id))


@user_bp.route("/payment/vnpay/callback")
def vnpay_callback():
    callback_data = request.args.to_dict(flat=True)
    gateway = VNPayGateway(current_app)

    if not gateway.verify_callback(callback_data):
        flash("Xác thực thanh toán thất bại.", "error")
        return redirect(url_for("user.user_index"))

    txn_ref = callback_data.get("vnp_TxnRef", "")
    response_code = callback_data.get("vnp_ResponseCode", "")
    transaction_no = callback_data.get("vnp_TransactionNo", "")

    payment = Payment.query.filter_by(vnp_txn_ref=txn_ref).first()
    if not payment:
        flash("Không tìm thấy giao dịch thanh toán.", "error")
        return redirect(url_for("user.user_index"))

    order = Order.query.get(payment.order_id)
    if not order:
        flash("Không tìm thấy đơn hàng.", "error")
        return redirect(url_for("user.user_index"))

    payment.vnp_transaction_no = transaction_no
    payment.vnp_response_code = response_code

    if response_code == "00":
        payment.payment_status = "completed"

        # VNPay success only confirms payment, delivery must still be confirmed by user.
        if order.status not in {"completed", "cancelled"}:
            order.status = "pending"

        cart = Cart.query.filter_by(user_id=order.user_id).first()
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()

        db.session.commit()
        flash("Thanh toán VNPay thành công. Vui lòng xác nhận khi đã nhận hàng.", "success")
        return redirect(url_for("user.user_index"))

    payment.payment_status = "failed"
    order.status = "cancelled"

    # Roll back reserved stock when VNPay payment fails.
    for item in order.items:
        variant = ProductVariant.query.get(item.variant_id) if item.variant_id else _find_variant_for_cart_item(item.product_id, None)
        if not variant:
            continue
        variant.stock = int(variant.stock or 0) + int(item.quantity or 0)
        _refresh_product_availability(item.product_id)

    db.session.commit()
    flash("Thanh toán VNPay không thành công.", "error")
    return redirect(url_for("user.checkout"))
