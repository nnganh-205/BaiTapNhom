from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# --- ĐIỀU HƯỚNG ---
@app.route('/')
def root():
    # Khi bạn vào 127.0.0.1:5000, nó sẽ tự nhảy sang trang Tổng quan
    return redirect(url_for('admin_index'))

# 1. Trang chủ (Tổng quan)
@app.route('/admin/')
def admin_index():
    return render_template('admin/index.html')

# 2. Trang Sản phẩm
@app.route('/admin/products')
def admin_products():
    return render_template('admin/products.html')

# 3. Trang Danh mục
@app.route('/admin/categories')
def admin_categories():
    # Mình để mảng rỗng [] nếu bạn muốn test giao diện "Chưa có dữ liệu"
    # Hoặc giữ nguyên list cũ của bạn để xem bảng có dữ liệu
    categories = [
        {"name": "Gà rán", "code": "GA01", "quantity": 12, "date": "06/04/2026"},
        {"name": "Burger", "code": "BG01", "quantity": 8, "date": "06/04/2026"}
    ]
    return render_template('admin/categories.html', categories=categories)

# 4. Trang Đơn hàng
@app.route('/admin/orders')
def admin_orders():
    # Lưu ý: file HTML của bạn đang tên là order.html (số ít)
    # nên để tên này cho chính xác với file trong thư mục templates
    return render_template('admin/order.html')

# 5. Trang Góp ý (Feedback)
@app.route('/admin/feedback')
def admin_feedback():
    return render_template('admin/feedback.html')

# 6. Trang Thống kê (Reports)
@app.route('/admin/reports')
def admin_reports():
    return render_template('admin/reports.html')

if __name__ == '__main__':
    # Chạy trên cổng 5000 và tự động load lại khi sửa code (debug=True)
    app.run(debug=True)