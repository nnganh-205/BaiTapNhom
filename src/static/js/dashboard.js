// Hàm này để click vào thì mở/đóng menu
function toggleUserMenu(event) {
    // Ngăn chặn sự kiện click lan ra ngoài (không làm đóng menu ngay lập tức)
    event.stopPropagation();

    const menu = document.getElementById('userMenu');
    const arrow = document.getElementById('arrowIcon');

    if (menu) {
        // Sử dụng 'active' cho đồng bộ với CSS mới nhất
        menu.classList.toggle('active');

        // Xoay mũi tên
        if (menu.classList.contains('active')) {
            arrow.style.transform = 'rotate(180deg)';
        } else {
            arrow.style.transform = 'rotate(0deg)';
        }
    }
}

// Lắng nghe sự kiện click toàn trang để đóng menu khi nhấn ra ngoài
document.addEventListener('click', function(e) {
    const menu = document.getElementById('userMenu');
    const arrow = document.getElementById('arrowIcon');
    const dropdown = document.getElementById('userDropdown');

    // Nếu click ra ngoài vùng dropdown thì đóng menu
    if (menu && dropdown && !dropdown.contains(e.target)) {
        menu.classList.remove('active');
        if (arrow) arrow.style.transform = 'rotate(0deg)';
    }
});