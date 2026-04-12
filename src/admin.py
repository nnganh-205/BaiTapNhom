import random
from flask import Blueprint, render_template,jsonify, redirect, request
from sqlalchemy import or_
from datetime import datetime
from . import db
from .models import User, Category, Product, ProductVariant, Order, Review, OrderItem

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
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
    # Lấy TẤT CẢ đơn hàng đã giao thành công (completed)
    orders = Order.query.filter_by(status='completed').all()

    # 1. Xác định thời gian hiện tại
    now = datetime.now()
    thang_nay = now.month
    nam_nay = now.year

    if thang_nay == 1:
        thang_truoc = 12
        nam_truoc = nam_nay - 1
    else:
        thang_truoc = thang_nay - 1
        nam_truoc = nam_nay

    # Các biến lưu tổng tiền
    doanh_thu_ky_nay = 0
    doanh_thu_ky_truoc = 0
    
    # Biến gom dữ liệu vẽ biểu đồ 12 tháng
    doanh_thu_12_thang = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
    
    # Biến gom thống kê theo từng sản phẩm
    thong_ke_sp = {}

    # 2. Vòng lặp 
    for don in orders:
        if don.created_at:
            # Tính doanh thu kỳ này vs kỳ trước
            if don.created_at.month == thang_nay and don.created_at.year == nam_nay:
                doanh_thu_ky_nay += don.total_price
            elif don.created_at.month == thang_truoc and don.created_at.year == nam_truoc:
                doanh_thu_ky_truoc += don.total_price
            
            # Gom doanh thu vào biểu đồ nếu cùng năm nay
            if don.created_at.year == nam_nay:
                doanh_thu_12_thang[don.created_at.month] += float(don.total_price)

        # 3. Lấy chi tiết từng món trong đơn để thống kê Sản phẩm
        # 3. Lấy chi tiết từng món trong đơn để thống kê Sản phẩm
        for item in don.items:
            san_pham = Product.query.get(item.product_id)
            ten_sp = san_pham.name if san_pham else "Sản phẩm đã xóa"
            
            
            if ten_sp not in thong_ke_sp:
                thong_ke_sp[ten_sp] = {'so_luong': 0, 'doanh_thu': 0}
                
            thong_ke_sp[ten_sp]['so_luong'] += item.quantity
            thong_ke_sp[ten_sp]['doanh_thu'] += float(item.price_at_purchase * item.quantity)

    # 4. Chuyển đổi dữ liệu thống kê sản phẩm thành dạng List và sắp xếp giảm dần
    list_thong_ke_sp = []
    for ten, data in thong_ke_sp.items():
        list_thong_ke_sp.append({
            'name': ten,
            'so_luong': data['so_luong'],
            'doanh_thu': data['doanh_thu']
        })
    list_thong_ke_sp = sorted(list_thong_ke_sp, key=lambda x: x['doanh_thu'], reverse=True)

    # 5. Tính phần trăm tăng trưởng
    if doanh_thu_ky_truoc > 0:
        tang_truong = ((doanh_thu_ky_nay - doanh_thu_ky_truoc) / doanh_thu_ky_truoc) * 100
        tang_truong = round(tang_truong, 1)
    else:
        tang_truong = 100 if doanh_thu_ky_nay > 0 else 0

    return render_template('admin/reports.html', 
                           dt_nay=doanh_thu_ky_nay, 
                           dt_truoc=doanh_thu_ky_truoc, 
                           tang_truong=tang_truong,
                           chart_data=list(doanh_thu_12_thang.values()), 
                           list_thong_ke_sp=list_thong_ke_sp)