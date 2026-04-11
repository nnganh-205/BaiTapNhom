document.addEventListener('DOMContentLoaded', function() {
    // 1. Khởi tạo Biểu đồ đường rỗng (Line Chart)
    initEmptyRevenueChart();

    // 2. Xử lý sự kiện Click chuyển Tab
    const tabs = document.querySelectorAll('.report-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Lấy loại dữ liệu từ thuộc tính data-type
            const type = this.getAttribute('data-type');
            switchReportTab(type, this);
        });
    });
});

function initEmptyRevenueChart() {
    const ctx = document.getElementById('revenueChart').getContext('2d');

    // Kiểm tra nếu canvas tồn tại để tránh lỗi
    if (!ctx) return;

    new Chart(ctx, {
        type: 'line', // Biểu đồ đường
        data: {
            // Nhãn trục X rỗng
            labels: ['', '', '', '', '', '', ''],
            datasets: [
                {
                    label: 'Kỳ này',
                    data: [0, 0, 0, 0, 0, 0, 0], // Dữ liệu rỗng
                    borderColor: '#3b82f6', // Xanh dương
                    backgroundColor: 'rgba(59, 130, 246, 0.05)',
                    fill: true, // Tô nền
                    tension: 0.4 // Bo tròn đường
                },
                {
                    label: 'Kỳ trước',
                    data: [0, 0, 0, 0, 0, 0, 0], // Dữ liệu rỗng
                    borderColor: '#94a3b8', // Xám
                    borderDash: [5, 5], // Đường đứt nét
                    fill: false, // Không tô nền
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // Ẩn legend mặc định, dùng legend tự chế trong HTML
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#9ca3af' }, // Màu chữ trục Y
                    grid: { color: '#f3f4f6' }  // Màu lưới trục Y
                },
                x: {
                    grid: { display: false } // Ẩn lưới trục X
                }
            }
        }
    });
}

function switchReportTab(type, element) {
    // 1. Cập nhật trạng thái Active cho Tab được nhấn
    document.querySelectorAll('.report-tab').forEach(t => t.classList.remove('active'));
    element.classList.add('active');

    // 2. Cập nhật tiêu đề bảng và tiêu đề cột dựa trên Tab
    const title = document.getElementById('table-title');
    const colName = document.getElementById('col-name');

    switch(type) {
        case 'product':
            title.innerText = "Chi tiết theo sản phẩm";
            colName.innerText = "Tên sản phẩm";
            break;
        case 'category':
            title.innerText = "Chi tiết theo danh mục";
            colName.innerText = "Tên danh mục";
            break;
        case 'staff':
            title.innerText = "Chi tiết theo nhân viên";
            colName.innerText = "Tên nhân viên";
            break;
    }

    // 3. (Mở rộng sau này) Tại đây bạn sẽ gọi AJAX để lấy dữ liệu trống thật của từng tab
    console.log("Đang chờ dữ liệu thực của Tab: " + type);
}