/**
 * main.js - Xử lý UI chung cho Client
 */

document.addEventListener('DOMContentLoaded', function() {

    // 1. Xử lý Toggle Menu Mobile
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }

    // 2. Xử lý Chatbot
    const chatBubble = document.getElementById('chat-bubble');
    const chatWindow = document.getElementById('chat-window');
    const openIco = document.getElementById('bubble-icon-open');
    const closeIco = document.getElementById('bubble-icon-close');

    if (chatBubble && chatWindow) {
        chatBubble.addEventListener('click', function() {
            chatWindow.classList.toggle('open');
            const isOpen = chatWindow.classList.contains('open');
            if (openIco) openIco.style.display = isOpen ? "none" : "block";
            if (closeIco) closeIco.style.display = isOpen ? "block" : "none";
        });
    }

    // 3. Hiệu ứng Navbar khi cuộn trang
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar-client');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.style.padding = "10px 0";
                navbar.style.boxShadow = "0 5px 20px rgba(0,0,0,0.1)";
            } else {
                navbar.style.padding = "15px 0";
                navbar.style.boxShadow = "none";
            }
        }
    });

    // 4. Gán sự kiện cho nút "Thêm sản phẩm" (FIX CHUẨN)
    const btnAdd = document.getElementById('btnAddProduct');
    if (btnAdd) {
        btnAdd.addEventListener('click', function() {
            toggleModal();
        });
    }
});


/**
 * Tự động vẽ lại phân trang dựa trên số liệu từ Backend
 */
function updatePagination(current, total) {
    const container = document.getElementById('page-numbers-container');
    const infoCurrent = document.getElementById('current-page-display');
    const infoTotal = document.getElementById('total-pages-display');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');

    if (!container) return;

    // Cập nhật text
    if (infoCurrent) infoCurrent.innerText = current;
    if (infoTotal) infoTotal.innerText = total;

    // Vẽ nút số
    let html = '';
    for (let i = 1; i <= total; i++) {
        html += `<button class="page-num ${i === current ? 'active' : ''}">${i}</button>`;
    }
    container.innerHTML = html;

    // Xử lý trạng thái nút Trước/Sau
    if (prevBtn) {
        if (current === 1) prevBtn.classList.add('disabled');
        else prevBtn.classList.remove('disabled');
    }

    if (nextBtn) {
        if (current === total) nextBtn.classList.add('disabled');
        else nextBtn.classList.remove('disabled');
    }
}


/**
 * Hàm đóng/mở Giỏ hàng Side Cart
 */
function toggleCart() {
    const cart = document.getElementById('sideCart');
    const overlay = document.getElementById('cartOverlay');

    if (cart && overlay) {
        cart.classList.toggle('active');
        overlay.classList.toggle('active');

        if (cart.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'auto';
        }
    }
}


/**
 * Modal thêm sản phẩm
 */
function toggleModal() {
    const modal = document.getElementById('addProductModal');
    if (modal) {
        modal.classList.toggle('show');

        if (modal.classList.contains('show')) {
            modal.style.display = 'flex';
        } else {
            modal.style.display = 'none';
        }
    }
}


/**
 * Preview ảnh khi upload
 */
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    if (input.files && input.files[0] && preview) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" style="width:100%; height:100%; object-fit:cover; border-radius:8px;">`;
        };
        reader.readAsDataURL(input.files[0]);
    }
}


/**
 * Click ra ngoài modal để đóng
 */
window.onclick = function(event) {
    const modal = document.getElementById('addProductModal');
    if (event.target === modal) {
        toggleModal();
    }
};