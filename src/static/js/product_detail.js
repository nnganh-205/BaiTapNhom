/**
 * product_detail.js - Xử lý Modal sản phẩm
 */
function openProductModal(name, price, img, desc) {
    const modal = document.getElementById('productModal');

    // Kiểm tra xem các element có tồn tại không trước khi gán
    const nameEl = document.getElementById('modalName');
    const priceEl = document.getElementById('modalPrice');
    const imgEl = document.getElementById('modalImg');
    const descEl = document.getElementById('modalDesc');
    const qtyEl = document.getElementById('modalQty');

    if (modal && nameEl && priceEl) {
        nameEl.innerText = name;
        priceEl.innerText = new Intl.NumberFormat('vi-VN').format(price) + '₫';
        imgEl.src = img;
        descEl.innerText = desc || "Hương vị thơm ngon khó cưỡng.";
        qtyEl.value = 1;

        // Thêm class để hiện Modal
        modal.classList.add('show');
        document.body.style.overflow = 'hidden'; // Chặn cuộn trang
    }
}

function closeModal() {
    const modal = document.getElementById('productModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto'; // Mở lại cuộn trang
    }
}

function changeQty(amt) {
    const qtyInput = document.getElementById('modalQty');
    if (qtyInput) {
        let val = parseInt(qtyInput.value) + amt;
        if (val < 1) val = 1;
        qtyInput.value = val;
    }
}

// Đóng modal khi click ra ngoài
window.addEventListener('click', function(e) {
    const modal = document.getElementById('productModal');
    if (e.target === modal) {
        closeModal();
    }
});