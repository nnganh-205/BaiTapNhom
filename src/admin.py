import random
import csv
import io
from flask import Blueprint, render_template,jsonify, redirect, request, flash, url_for, Response
from flask_login import current_user
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from . import db
from .models import User, Category, Product, ProductVariant, Order, Review, OrderItem, Payment
from .promotions import load_promotions, save_promotions

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def _variant_sale_price(variant: ProductVariant | None) -> float:
    if not variant:
        return 0.0
    base_price = float(variant.price or 0)
    percent = float(variant.discount_percent or 0)
    percent = max(0.0, min(100.0, percent))
    return round(base_price * (1 - percent / 100.0), 2)


@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated:
        flash('Vui long dang nhap de vao trang quan tri.', 'error')
        return redirect(url_for('auth.login'))
    if current_user.role != 'admin':
        flash('Ban khong co quyen truy cap trang quan tri.', 'error')
        return redirect(url_for('user.user_index'))

# Hiển thị người dùng
@admin_bp.route('/')
def admin_index():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)

    query = User.query

    if search_query:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%"),
                User.phone.ilike(f"%{search_query}%")
            )
        )

    # 3. Dù tìm kiếm hay không thì cũng phải Đóng gói & Phân trang
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
    users = pagination.items

    return render_template('admin/index.html', 
                           users=users, 
                           search_query=search_query, 
                           pagination=pagination)

# Xóa người dùng
@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "Đã xóa người dùng thành công!"})
    else:
        return jsonify({"success": False, "message": "Không tìm thấy người dùng!"}), 404
    
# Trang Sản phẩm
@admin_bp.route('/products')
def admin_products():
    categories = Category.query.all()
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Product.query.outerjoin(Category)
    if search_query:
        keyword = f"%{search_query}%"
        query = query.filter(
            or_(
                Product.name.ilike(keyword),
                Product.sku.ilike(keyword),
                Category.name.ilike(keyword),
            )
        )

    pagination = query.order_by(Product.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
    products = pagination.items
    return render_template(
        'admin/products.html',
        products=products,
        categories=categories,
        pagination=pagination,
        search_query=search_query,
    )
# Xử lý Thêm Sản phẩm
@admin_bp.route('/add-product', methods=['POST'])
def add_product():
    ten_mon = request.form.get('ten_mon')
    ma_sku = request.form.get('ma_sku')
    id_danh_muc = request.form.get('id_danh_muc')
    mo_ta = request.form.get('mo_ta')
    
    gia = request.form.get('gia')
    ton_kho = request.form.get('ton_kho')
    giam_phan_tram = request.form.get('giam_phan_tram', type=float) or 0
    giam_phan_tram = max(0.0, min(100.0, giam_phan_tram))

    file_anh = request.files.get('anh_san_pham')
    ten_file_anh = ""
    if file_anh:
        ten_file_anh = file_anh.filename 
      
    initial_stock = int(ton_kho or 0)
    san_pham_moi = Product(
        name=ten_mon,
        sku=ma_sku,
        category_id=id_danh_muc,
        description=mo_ta,
        image_url=ten_file_anh,
        is_available=initial_stock > 0,
    )
    db.session.add(san_pham_moi)
    db.session.flush()

    bien_the_moi = ProductVariant(
        product_id=san_pham_moi.id, 
        size_name="Mặc định",       
        price=gia,
        discount_percent=giam_phan_tram,
        stock=initial_stock
    )
    db.session.add(bien_the_moi)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('SKU đã tồn tại. Vui lòng dùng mã khác.', 'error')
        return redirect('/admin/products')

    return redirect('/admin/products')


@admin_bp.route('/update-product/<int:product_id>', methods=['POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    product.name = request.form.get('ten_mon', '').strip()
    product.sku = request.form.get('ma_sku', '').strip()
    product.category_id = request.form.get('id_danh_muc') or None
    product.description = request.form.get('mo_ta', '').strip()

    file_anh = request.files.get('anh_san_pham')
    if file_anh and file_anh.filename:
        product.image_url = file_anh.filename

    variant = product.variants[0] if product.variants else None
    if not variant:
        variant = ProductVariant(product_id=product.id, size_name='Mặc định', price=0, stock=0)
        db.session.add(variant)

    variant.price = request.form.get('gia', type=float) or 0
    variant.discount_percent = max(0.0, min(100.0, request.form.get('giam_phan_tram', type=float) or 0))
    variant.stock = request.form.get('ton_kho', type=int) or 0
    product.is_available = variant.stock > 0

    try:
        db.session.commit()
        flash('Đã cập nhật sản phẩm thành công.', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Mã SKU đã tồn tại. Vui lòng chọn mã khác.', 'error')

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    return redirect(url_for('admin.admin_products', page=page, search=search))

# Xử lý Xóa Sản phẩm
@admin_bp.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    san_pham = Product.query.get(product_id)
    
    if san_pham:
        db.session.delete(san_pham)
        db.session.commit()
        return jsonify({"success": True, "message": "Đã xóa thành công!"})
        
    return jsonify({"success": False, "message": "Không tìm thấy!"})

# Trang Danh mục
@admin_bp.route('/categories')
def admin_categories():
    page = request.args.get('page', 1, type=int)
    pagination = Category.query.paginate(page=page, per_page=5, error_out=False)
    categories = pagination.items
    return render_template('admin/categories.html', categories=categories, pagination=pagination)


@admin_bp.route('/categories/<int:category_id>')
def admin_category_detail(category_id):
    category = Category.query.get_or_404(category_id)
    products = Product.query.filter_by(category_id=category.id).order_by(Product.created_at.desc()).all()

    product_rows = []
    for product in products:
        variants = product.variants or []
        total_stock = sum(int(variant.stock or 0) for variant in variants)
        min_price = min((_variant_sale_price(variant) for variant in variants), default=0.0)

        product_rows.append(
            {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'price': min_price,
                'stock': total_stock,
                'is_available': bool(product.is_available and total_stock > 0),
                'created_at': product.created_at,
            }
        )

    return render_template('admin/category_detail.html', category=category, product_rows=product_rows)


@admin_bp.route('/categories/<int:category_id>/update', methods=['POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)

    name = (request.form.get('ten_danh_muc') or '').strip()
    code = (request.form.get('ma_danh_muc') or '').strip()
    description = (request.form.get('mo_ta') or '').strip()

    if not name or not code:
        flash('Tên danh mục và mã danh mục là bắt buộc.', 'error')
        return redirect(url_for('admin.admin_category_detail', category_id=category.id))

    category.name = name
    category.category_code = code
    category.description = description

    try:
        db.session.commit()
        flash('Đã cập nhật danh mục thành công.', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Mã danh mục đã tồn tại. Vui lòng chọn mã khác.', 'error')

    return redirect(url_for('admin.admin_category_detail', category_id=category.id))
# 2. Xử lý Thêm Danh mục mới
@admin_bp.route('/add-category', methods=['POST'])
def add_category():
    ten_dm = request.form.get('ten_danh_muc')
    ma_dm = request.form.get('ma_danh_muc')
    mo_ta = request.form.get('mo_ta')

    danh_muc_moi = Category(
        name=ten_dm,
        category_code=ma_dm,
        description=mo_ta
    )
    
    db.session.add(danh_muc_moi)
    db.session.commit()

    return redirect('/admin/categories')

@admin_bp.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    danh_muc = Category.query.get(category_id)
    if danh_muc:
        db.session.delete(danh_muc)
        db.session.commit()
        return jsonify({"success": True, "message": "Đã xóa danh mục thành công!"})
        
    return jsonify({"success": False, "message": "Không tìm thấy danh mục!"})

# Trang danh sách Đơn hàng 
@admin_bp.route('/orders')
def admin_orders():
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Order.query.outerjoin(User)
    
    if search_query:
        query = query.filter(
            or_(
                Order.order_code.ilike(f"%{search_query}%"),
                User.full_name.ilike(f"%{search_query}%")
            )
        )
   
    pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
    orders = pagination.items
    all_users = User.query.filter(User.role != 'admin').all()
    all_products = Product.query.all()
    order_ids = [order.id for order in orders]
    order_item_rows = []
    if order_ids:
        order_item_rows = (
            db.session.query(OrderItem.order_id, Product.name, OrderItem.quantity)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(OrderItem.order_id.in_(order_ids))
            .all()
        )
    order_item_map = {order_id: [] for order_id in order_ids}
    for row in order_item_rows:
        order_item_map.setdefault(row.order_id, []).append(f"{row.name} x{row.quantity}")

    return render_template('admin/order.html', 
                           orders=orders, 
                           pagination=pagination, 
                           search_query=search_query,
                           users=all_users,
                           products=all_products,
                           order_item_map=order_item_map)

# Xử lý Tạo đơn hàng mới từ Modal
@admin_bp.route('/add-order', methods=['POST'])
def add_order():
    user_id = request.form.get('khach_hang_id')
    product_id = request.form.get('san_pham_id')
    dia_chi = request.form.get('dia_chi')
    ghi_chu = request.form.get('ghi_chu')
    
    so_luong = int(request.form.get('so_luong', 1))
    if so_luong < 1:
        flash('Số lượng không hợp lệ.', 'error')
        return redirect('/admin/orders')

    product = Product.query.get(product_id)
    variant = product.variants[0] if product and product.variants else None
    if not product or not variant:
        flash('Sản phẩm không hợp lệ hoặc chưa có biến thể giá.', 'error')
        return redirect('/admin/orders')

    if (variant.stock or 0) < so_luong:
        flash(f"Tồn kho không đủ cho {product.name}. Còn lại: {variant.stock or 0}", 'error')
        return redirect('/admin/orders')

    price_each = _variant_sale_price(variant)

    total = float(price_each) * so_luong
    
    code = f"ORD-{random.randint(10000, 99999)}"

    new_order = Order(
        order_code=code,
        user_id=user_id if user_id else None,
        total_price=total,
        status='pending', 
        shipping_address=dia_chi,
        note=ghi_chu
    )
    db.session.add(new_order)
    db.session.flush()

    detail = OrderItem(
        order_id=new_order.id,
        product_id=product_id,
        variant_id=variant.id,
        quantity=so_luong,
        price_at_purchase=price_each
    )
    db.session.add(detail)

    variant.stock = int(variant.stock or 0) - so_luong
    product.is_available = any((v.stock or 0) > 0 for v in product.variants)

    db.session.commit()
    flash('Đã tạo đơn hàng và cập nhật tồn kho.', 'success')

    return redirect('/admin/orders')

# Xử lý Xóa đơn hàng
@admin_bp.route('/delete-order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    don_hang = Order.query.get(order_id)
    if don_hang:
        db.session.delete(don_hang)
        db.session.commit()
        return jsonify({"success": True, "message": "Đã xóa đơn hàng thành công!"})
        
    return jsonify({"success": False, "message": "Không tìm thấy đơn!"})

@admin_bp.route('/update-order-status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    don_hang = Order.query.get(order_id)
    
    if don_hang:
        if don_hang.status == 'pending':
            don_hang.status = 'completed'
        else:
            don_hang.status = 'pending'
            
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Đã cập nhật trạng thái đơn hàng!", 
            "new_status": don_hang.status
        })
        
    return jsonify({"success": False, "message": "Không tìm thấy đơn hàng!"})
# Trang feedback
@admin_bp.route('/feedback')
def admin_feedback():
    all_reviews = Review.query.all()
    
    total_reviews = len(all_reviews)
    new_feedback_count = 0
    tong_diem = 0
    
    for r in all_reviews:
        if r.is_read == False: 
            new_feedback_count += 1
        
        if r.rating: 
            tong_diem += r.rating
            
    if total_reviews > 0:
        avg_rating = round(tong_diem / total_reviews, 1)
    else:
        avg_rating = 0.0

    page = request.args.get('page', 1, type=int)
    pagination = Review.query.order_by(Review.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
    reviews = pagination.items

    return render_template('admin/feedback.html', 
                           reviews=reviews,
                           pagination=pagination,
                           new_feedback_count=new_feedback_count,
                           avg_rating=avg_rating,
                           total_reviews=total_reviews)

# Route Xử lý "Đánh dấu đã đọc"
@admin_bp.route('/read-feedback/<int:review_id>', methods=['POST'])
def read_feedback(review_id):
    review = Review.query.get(review_id)
    if review:
        review.is_read = True
        db.session.commit()
        return jsonify({"success": True, "message": "Đã đánh dấu đọc!"})
    return jsonify({"success": False})

# Xóa Feedback
@admin_bp.route('/delete-feedback/<int:review_id>', methods=['POST'])
def delete_feedback(review_id):
    review = Review.query.get(review_id)
    if review:
        db.session.delete(review)
        db.session.commit()
        return jsonify({"success": True, "message": "Đã xóa phản hồi!"})
    return jsonify({"success": False})


@admin_bp.route('/promotions')
def admin_promotions():
    promotions = load_promotions()
    return render_template('admin/promotions.html', promotions=promotions)


@admin_bp.route('/promotions/create', methods=['POST'])
def create_promotion():
    promotions = load_promotions()

    code = (request.form.get('code', '') or '').strip().upper()
    name = (request.form.get('name', '') or '').strip()
    promo_type = (request.form.get('type', '') or '').strip()
    discount_mode = (request.form.get('discount_mode', '') or '').strip()

    if not code or not name or promo_type not in {'free_ship', 'fixed_discount', 'group_combo', 'lucky_hour'}:
        flash('Vui lòng nhập đầy đủ thông tin cơ bản của khuyến mại.', 'error')
        return redirect(url_for('admin.admin_promotions'))

    if any(str(item.get('code', '')).upper() == code for item in promotions):
        flash(f'Mã {code} đã tồn tại.', 'error')
        return redirect(url_for('admin.admin_promotions'))

    def _to_non_negative_int(field_name: str, default: int = 0) -> int:
        raw = (request.form.get(field_name, '') or '').strip()
        if raw == '':
            return default
        try:
            return max(0, int(raw))
        except ValueError:
            return default

    new_item = {
        'code': code,
        'name': name,
        'type': promo_type,
        'enabled': request.form.get('enabled') == 'on',
        'min_subtotal': _to_non_negative_int('min_subtotal', 0),
    }

    if promo_type in {'fixed_discount', 'group_combo'}:
        if discount_mode not in {'amount', 'percent'}:
            discount_mode = 'amount'
        new_item['discount_mode'] = discount_mode
        if discount_mode == 'percent':
            new_item['discount_percent'] = min(100, _to_non_negative_int('discount_percent', 0))
            new_item['discount_amount'] = 0
        else:
            new_item['discount_amount'] = _to_non_negative_int('discount_amount', 0)
            new_item['discount_percent'] = 0
    if promo_type == 'group_combo':
        new_item['min_items'] = max(1, _to_non_negative_int('min_items', 1))
    if promo_type == 'lucky_hour':
        new_item['discount_percent'] = min(100, _to_non_negative_int('lucky_discount_percent', 0))
        new_item['min_stock'] = _to_non_negative_int('min_stock', 0)
        window_text = (request.form.get('time_windows', '') or '').strip()
        windows = []
        if window_text:
            for chunk in window_text.split(','):
                item = chunk.strip()
                if '-' not in item:
                    continue
                start, end = item.split('-', 1)
                try:
                    start_h = int(start)
                    end_h = int(end)
                except ValueError:
                    continue
                if 0 <= start_h <= 23 and 1 <= end_h <= 24 and start_h < end_h:
                    windows.append([start_h, end_h])
        new_item['time_windows'] = windows or [[6, 12], [13, 15]]

    promotions.append(new_item)
    save_promotions(promotions)
    flash(f'Đã thêm khuyến mại {code}.', 'success')
    return redirect(url_for('admin.admin_promotions'))


@admin_bp.route('/promotions/update/<string:promo_code>', methods=['POST'])
def update_promotion(promo_code):
    promotions = load_promotions()
    target = None
    for promo in promotions:
        if str(promo.get('code', '')).upper() == promo_code.upper():
            target = promo
            break

    if not target:
        flash('Không tìm thấy khuyến mại.', 'error')
        return redirect(url_for('admin.admin_promotions'))

    target['enabled'] = request.form.get('enabled') == 'on'
    if target.get('type') in {'fixed_discount', 'group_combo'}:
        requested_mode = (request.form.get('discount_mode', '') or '').strip()
        if requested_mode in {'amount', 'percent'}:
            target['discount_mode'] = requested_mode

    for int_field in ['min_subtotal', 'discount_amount', 'min_items', 'discount_percent', 'min_stock']:
        raw = request.form.get(int_field, '').strip()
        if raw == '':
            continue
        try:
            target[int_field] = max(0, int(raw))
        except ValueError:
            flash(f'Giá trị {int_field} không hợp lệ.', 'error')
            return redirect(url_for('admin.admin_promotions'))

    if target.get('type') in {'fixed_discount', 'group_combo'}:
        mode = target.get('discount_mode')
        if mode == 'percent':
            target['discount_amount'] = 0
            target['discount_percent'] = min(100, int(target.get('discount_percent', 0) or 0))
        elif mode == 'amount':
            target['discount_percent'] = 0

    window_text = request.form.get('time_windows', '').strip()
    if window_text:
        windows = []
        for chunk in window_text.split(','):
            item = chunk.strip()
            if '-' not in item:
                continue
            start, end = item.split('-', 1)
            try:
                start_h = int(start)
                end_h = int(end)
            except ValueError:
                continue
            if 0 <= start_h <= 23 and 1 <= end_h <= 24 and start_h < end_h:
                windows.append([start_h, end_h])
        if windows:
            target['time_windows'] = windows

    save_promotions(promotions)
    flash(f"Đã cập nhật khuyến mại {target.get('code', '')}.", 'success')
    return redirect(url_for('admin.admin_promotions'))


@admin_bp.route('/promotions/delete/<string:promo_code>', methods=['POST'])
def delete_promotion(promo_code):
    promotions = load_promotions()
    before_count = len(promotions)
    filtered = [
        promo for promo in promotions
        if str(promo.get('code', '')).upper() != promo_code.upper()
    ]

    if len(filtered) == before_count:
        return jsonify({'success': False, 'message': 'Không tìm thấy mã khuyến mại.'}), 404

    save_promotions(filtered)
    return jsonify({'success': True, 'message': f'Đã xóa mã {promo_code.upper()}.'})


def _build_reports_payload(args) -> dict:
    def parse_date(value, default_date):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date() if value else default_date
        except ValueError:
            return default_date

    def parse_year(value, default_year):
        try:
            year = int(value)
            return year if 2000 <= year <= 2100 else default_year
        except (TypeError, ValueError):
            return default_year

    today = datetime.now().date()
    default_from = today.replace(day=1)
    report_mode = args.get('mode', 'range')
    if report_mode not in {'range', 'year'}:
        report_mode = 'range'
    selected_year = parse_year(args.get('year'), today.year)

    start_date = parse_date(args.get('from'), default_from)
    end_date = parse_date(args.get('to'), today)
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    group_by = args.get('group_by', 'day')
    if group_by not in {'day', 'week', 'month', 'year'}:
        group_by = 'day'

    if report_mode == 'year':
        start_date = datetime(selected_year, 1, 1).date()
        end_date = datetime(selected_year, 12, 31).date()
        prev_start_date = datetime(selected_year - 1, 1, 1).date()
        prev_end_date = datetime(selected_year - 1, 12, 31).date()
        group_by = 'month'
    else:
        period_days = (end_date - start_date).days + 1
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=period_days - 1)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt_exclusive = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
    prev_start_dt = datetime.combine(prev_start_date, datetime.min.time())
    prev_end_dt_exclusive = datetime.combine(prev_end_date + timedelta(days=1), datetime.min.time())

    paid_statuses = {'completed', 'success'}

    base_paid_query = (
        db.session.query(Order)
        .join(Payment, Payment.order_id == Order.id)
        .filter(Payment.payment_status.in_(paid_statuses))
        .filter(Order.status != 'cancelled')
    )

    doanh_thu_ky_nay = float(
        base_paid_query
        .filter(Payment.created_at >= start_dt, Payment.created_at < end_dt_exclusive)
        .with_entities(func.coalesce(func.sum(Payment.amount), 0))
        .scalar()
        or 0
    )
    doanh_thu_ky_truoc = float(
        base_paid_query
        .filter(Payment.created_at >= prev_start_dt, Payment.created_at < prev_end_dt_exclusive)
        .with_entities(func.coalesce(func.sum(Payment.amount), 0))
        .scalar()
        or 0
    )

    if doanh_thu_ky_truoc > 0:
        tang_truong = round(((doanh_thu_ky_nay - doanh_thu_ky_truoc) / doanh_thu_ky_truoc) * 100, 1)
    else:
        tang_truong = 100 if doanh_thu_ky_nay > 0 else 0

    bucket_expr = func.strftime('%Y-%m-%d', Payment.created_at)
    if group_by == 'week':
        bucket_expr = func.strftime('%Y-W%W', Payment.created_at)
    elif group_by == 'month':
        bucket_expr = func.strftime('%Y-%m', Payment.created_at)
    elif group_by == 'year':
        bucket_expr = func.strftime('%Y', Payment.created_at)

    timeline_query_rows = (
        db.session.query(
            bucket_expr.label('bucket'),
            func.count(func.distinct(Order.id)).label('paid_orders'),
            func.coalesce(func.sum(Payment.amount), 0).label('revenue'),
        )
        .join(Payment, Payment.order_id == Order.id)
        .filter(Payment.payment_status.in_(paid_statuses))
        .filter(Order.status != 'cancelled')
        .filter(Payment.created_at >= start_dt, Payment.created_at < end_dt_exclusive)
        .group_by(bucket_expr)
        .order_by(bucket_expr.asc())
        .all()
    )

    timeline_rows = []
    chart_labels = []
    chart_data = []

    if report_mode == 'year':
        timeline_map = {row.bucket: row for row in timeline_query_rows}
        for month in range(1, 13):
            bucket = f'{selected_year}-{month:02d}'
            row = timeline_map.get(bucket)
            paid_orders = int(row.paid_orders) if row else 0
            revenue = float(row.revenue or 0) if row else 0.0
            timeline_rows.append({'bucket': f'Tháng {month}', 'paid_orders': paid_orders, 'revenue': revenue})
            chart_labels.append(f'T{month}')
            chart_data.append(revenue)
    else:
        for row in timeline_query_rows:
            timeline_rows.append(
                {
                    'bucket': row.bucket,
                    'paid_orders': int(row.paid_orders or 0),
                    'revenue': float(row.revenue or 0),
                }
            )
        chart_labels = [row['bucket'] for row in timeline_rows]
        chart_data = [row['revenue'] for row in timeline_rows]

    product_query_rows = (
        db.session.query(
            Product.name.label('name'),
            func.coalesce(func.sum(OrderItem.quantity), 0).label('so_luong'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.price_at_purchase), 0).label('doanh_thu'),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .join(Payment, Payment.order_id == Order.id)
        .filter(Payment.payment_status.in_(paid_statuses))
        .filter(Order.status != 'cancelled')
        .filter(Payment.created_at >= start_dt, Payment.created_at < end_dt_exclusive)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(OrderItem.quantity * OrderItem.price_at_purchase).desc())
        .all()
    )

    list_thong_ke_sp = [
        {
            'name': row.name,
            'so_luong': int(row.so_luong or 0),
            'doanh_thu': float(row.doanh_thu or 0),
        }
        for row in product_query_rows
    ]

    return {
        'dt_nay': doanh_thu_ky_nay,
        'dt_truoc': doanh_thu_ky_truoc,
        'tang_truong': tang_truong,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'timeline_rows': timeline_rows,
        'list_thong_ke_sp': list_thong_ke_sp,
        'filter_from': start_date.strftime('%Y-%m-%d'),
        'filter_to': end_date.strftime('%Y-%m-%d'),
        'filter_group_by': group_by,
        'filter_mode': report_mode,
        'filter_year': selected_year,
    }

# Báo cáo doanh thu
@admin_bp.route('/reports')
def admin_reports():
    payload = _build_reports_payload(request.args)
    return render_template('admin/reports.html', **payload)


@admin_bp.route('/reports/export-csv')
def admin_reports_csv():
    payload = _build_reports_payload(request.args)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['BAO CAO DOANH THU - INVENTORY'])
    writer.writerow(['Thoi gian xuat', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['Che do loc', 'Theo nam' if payload['filter_mode'] == 'year' else 'Tuy chinh'])
    writer.writerow(['Tu ngay', payload['filter_from']])
    writer.writerow(['Den ngay', payload['filter_to']])
    writer.writerow(['Nhom du lieu', payload['filter_group_by']])
    writer.writerow([])

    writer.writerow(['TONG QUAN'])
    writer.writerow(['Doanh thu da thanh toan', f"{payload['dt_nay']:.0f}"])
    writer.writerow(['Doanh thu ky so sanh', f"{payload['dt_truoc']:.0f}"])
    writer.writerow(['Ti le tang truong (%)', f"{payload['tang_truong']:.1f}"])
    writer.writerow([])

    writer.writerow(['DOANH THU THEO MOC THOI GIAN'])
    writer.writerow(['Moc thoi gian', 'So don da thanh toan', 'Doanh thu'])
    for row in payload['timeline_rows']:
        writer.writerow([row['bucket'], row['paid_orders'], f"{row['revenue']:.0f}"])
    writer.writerow([])

    writer.writerow(['TOP SAN PHAM BAN CHAY'])
    writer.writerow(['Ten san pham', 'So luong ban', 'Doanh thu'])
    for row in payload['list_thong_ke_sp']:
        writer.writerow([row['name'], row['so_luong'], f"{row['doanh_thu']:.0f}"])

    csv_data = '\ufeff' + output.getvalue()
    output.close()

    filename = f"bao_cao_doanh_thu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        csv_data,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename={filename}'},
    )
