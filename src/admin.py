import random
from flask import Blueprint, render_template,jsonify, redirect, request, flash, url_for
from flask_login import current_user
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from . import db
from .models import User, Category, Product, ProductVariant, Order, Review, OrderItem, Payment

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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
    page = request.args.get('page', 1, type=int)
    pagination = Product.query.paginate(page=page, per_page=8, error_out=False)
    products = pagination.items
    return render_template('admin/products.html', products=products, categories=categories, pagination=pagination)
# Xử lý Thêm Sản phẩm 
@admin_bp.route('/add-product', methods=['POST'])
def add_product():
    ten_mon = request.form.get('ten_mon')
    ma_sku = request.form.get('ma_sku')
    id_danh_muc = request.form.get('id_danh_muc')
    mo_ta = request.form.get('mo_ta')
    
    gia = request.form.get('gia')
    ton_kho = request.form.get('ton_kho')

    file_anh = request.files.get('anh_san_pham')
    ten_file_anh = ""
    if file_anh:
        ten_file_anh = file_anh.filename 
      
    san_pham_moi = Product(
        name=ten_mon,
        sku=ma_sku,
        category_id=id_danh_muc,
        description=mo_ta,
        image_url=ten_file_anh
    )
    db.session.add(san_pham_moi)
    db.session.commit() 
    
    bien_the_moi = ProductVariant(
        product_id=san_pham_moi.id, 
        size_name="Mặc định",       
        price=gia,
        stock=ton_kho
    )
    db.session.add(bien_the_moi)
    db.session.commit()
    return redirect('/admin/products')

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
    
    return render_template('admin/order.html', 
                           orders=orders, 
                           pagination=pagination, 
                           search_query=search_query,
                           users=all_users,
                           products=all_products)

# Xử lý Tạo đơn hàng mới từ Modal
@admin_bp.route('/add-order', methods=['POST'])
def add_order():
    user_id = request.form.get('khach_hang_id')
    product_id = request.form.get('san_pham_id')
    dia_chi = request.form.get('dia_chi')
    ghi_chu = request.form.get('ghi_chu')
    
    so_luong = int(request.form.get('so_luong', 1)) 

    product = Product.query.get(product_id)
    price_each = 0
    if product and product.variants:
        price_each = product.variants[0].price
    
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
    db.session.commit()

    detail = OrderItem(
        order_id=new_order.id,
        product_id=product_id,
        quantity=so_luong, 
        price_at_purchase=price_each
    )
    db.session.add(detail)
    db.session.commit()

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
# Báo cáo doanh thu
@admin_bp.route('/reports')
def admin_reports():
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
    report_mode = request.args.get('mode', 'range')
    if report_mode not in {'range', 'year'}:
        report_mode = 'range'
    selected_year = parse_year(request.args.get('year'), today.year)

    start_date = parse_date(request.args.get('from'), default_from)
    end_date = parse_date(request.args.get('to'), today)
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    group_by = request.args.get('group_by', 'day')
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

    timeline_rows = (
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

    if report_mode == 'year':
        timeline_map = {row.bucket: row for row in timeline_rows}
        normalized_rows = []
        chart_labels = []
        chart_data = []

        for month in range(1, 13):
            bucket = f'{selected_year}-{month:02d}'
            row = timeline_map.get(bucket)
            paid_orders = int(row.paid_orders) if row else 0
            revenue = float(row.revenue or 0) if row else 0.0
            normalized_rows.append({'bucket': f'Tháng {month}', 'paid_orders': paid_orders, 'revenue': revenue})
            chart_labels.append(f'T{month}')
            chart_data.append(revenue)

        timeline_rows = normalized_rows
    else:
        chart_labels = [row.bucket for row in timeline_rows]
        chart_data = [float(row.revenue or 0) for row in timeline_rows]

    list_thong_ke_sp = (
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

    return render_template(
        'admin/reports.html',
        dt_nay=doanh_thu_ky_nay,
        dt_truoc=doanh_thu_ky_truoc,
        tang_truong=tang_truong,
        chart_labels=chart_labels,
        chart_data=chart_data,
        timeline_rows=timeline_rows,
        list_thong_ke_sp=list_thong_ke_sp,
        filter_from=start_date.strftime('%Y-%m-%d'),
        filter_to=end_date.strftime('%Y-%m-%d'),
        filter_group_by=group_by,
        filter_mode=report_mode,
        filter_year=selected_year,
    )
