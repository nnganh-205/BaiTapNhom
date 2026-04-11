from flask import Blueprint,render_template
admin_bp = Blueprint('admin',__name__,url_prefix='/admin')

@admin_bp.route('/')
def admin_index():
    return render_template('admin/index.html')

# 2. Trang Sản phẩm
@admin_bp.route('/products')
def admin_products():
    return render_template('admin/products.html')

# 3. Trang Danh mục
@admin_bp.route('/categories')
def admin_categories():
    # Mình để mảng rỗng [] nếu bạn muốn test giao diện "Chưa có dữ liệu"
    # Hoặc giữ nguyên list cũ của bạn để xem bảng có dữ liệu
    categories = [
        {"name": "Gà rán", "code": "GA01", "quantity": 12, "date": "06/04/2026"},
        {"name": "Burger", "code": "BG01", "quantity": 8, "date": "06/04/2026"}
    ]
    return render_template('admin/categories.html', categories=categories)

# 4. Trang Đơn hàng
@admin_bp.route('/orders')
def admin_orders():
    # Lưu ý: file HTML của bạn đang tên là order.html (số ít)
    # nên để tên này cho chính xác với file trong thư mục templates
    return render_template('admin/order.html')

# 5. Trang Góp ý (Feedback)
@admin_bp.route('/feedback')
def admin_feedback():
    return render_template('admin/feedback.html')

# 6. Trang Thống kê (Reports)
@admin_bp.route('/reports')
def admin_reports():
    return render_template('admin/reports.html')