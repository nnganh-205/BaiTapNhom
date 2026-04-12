/**
 * product_detail.js - Xử lý Modal sản phẩm
 */
const LARGE_SIZE_EXTRA = 15000;

function getSelectedSize() {
    return document.querySelector('input[name="size"]:checked')?.value === 'L' ? 'L' : 'S';
}

function updateModalPriceBySize() {
    const modal = document.getElementById('productModal');
    const priceEl = document.getElementById('modalPrice');
    if (!modal || !priceEl) {
        return;
    }

    const basePrice = Number(modal.dataset.productPrice || 0);
    const size = getSelectedSize();
    const finalPrice = basePrice + (size === 'L' ? LARGE_SIZE_EXTRA : 0);
    priceEl.innerText = new Intl.NumberFormat('vi-VN').format(finalPrice) + '₫';
}

function openProductModal(productId, name, price, img, desc) {
    const modal = document.getElementById('productModal');

    // Kiểm tra xem các element có tồn tại không trước khi gán
    const nameEl = document.getElementById('modalName');
    const priceEl = document.getElementById('modalPrice');
    const imgEl = document.getElementById('modalImg');
    const descEl = document.getElementById('modalDesc');
    const qtyEl = document.getElementById('modalQty');

    if (modal && nameEl && priceEl) {
        modal.dataset.productId = String(productId || "");
        modal.dataset.productName = name || "Sản phẩm";
        modal.dataset.productImage = img || "";
        modal.dataset.productPrice = String(price || 0);
        nameEl.innerText = name;
        imgEl.src = img;
        descEl.innerText = desc || "Hương vị thơm ngon khó cưỡng.";
        qtyEl.value = 1;

        const sizeS = document.getElementById('sizeS');
        if (sizeS) {
            sizeS.checked = true;
        }
        updateModalPriceBySize();

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

function addToCartFromModal() {
    const modal = document.getElementById('productModal');
    const productName = document.getElementById('modalName')?.innerText || 'Sản phẩm';
    const qty = parseInt(document.getElementById('modalQty')?.value || '1', 10);
    const productId = parseInt(modal?.dataset.productId || '0', 10);
    const size = getSelectedSize();
    const sizeExtra = size === 'L' ? LARGE_SIZE_EXTRA : 0;
    const basePrice = Number(modal?.dataset.productPrice || 0);
    const finalPrice = basePrice + sizeExtra;
    const sizeLabel = size === 'L' ? 'To' : 'Vừa';

    if (!productId || !window.cartClient) {
        alert('Không thể thêm vào giỏ hàng lúc này.');
        return;
    }

    window.cartClient.addToCart(productId, qty, {
        name: modal?.dataset.productName || productName,
        image: modal?.dataset.productImage || "",
        price: finalPrice,
        size,
        sizeExtra,
    }).then(function (ok) {
        if (ok) {
            alert(`Đã thêm ${qty} ${productName} (size ${sizeLabel}) vào giỏ hàng.`);
            closeModal();
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    const sizeInputs = document.querySelectorAll('input[name="size"]');
    sizeInputs.forEach(function (input) {
        input.addEventListener('change', updateModalPriceBySize);
    });
});

// Đóng modal khi click ra ngoài
window.addEventListener('click', function(e) {
    const modal = document.getElementById('productModal');
    if (e.target === modal) {
        closeModal();
    }
});