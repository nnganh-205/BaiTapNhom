document.addEventListener("DOMContentLoaded", function () {
    const filterDataEl = document.getElementById("products-filters-data");
    const filterState = window.currentFilters || {
        search: filterDataEl?.dataset.search || "",
        category: filterDataEl?.dataset.category || "all",
        sort: filterDataEl?.dataset.sort || "newest",
        currentPage: parseInt(filterDataEl?.dataset.currentPage || "1", 10) || 1,
        totalPages: parseInt(filterDataEl?.dataset.totalPages || "1", 10) || 1,
    };

    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-input");
    const sortSelect = document.getElementById("sort");
    const categoryButtons = document.querySelectorAll(".category-badge[data-category]");
    const paginationButtons = document.querySelectorAll("button[data-page]");
    const bestItems = document.querySelectorAll(".best-item[data-focus-product]");

    // Use data-* payloads to keep template HTML free from inline JS expressions.
    document.addEventListener("click", function (event) {
        const openEl = event.target.closest(".js-open-product");
        if (openEl) {
            const productId = parseInt(openEl.dataset.productId || "0", 10);
            const productName = openEl.dataset.productName || "";
            const productPrice = parseFloat(openEl.dataset.productPrice || "0") || 0;
            const productImage = openEl.dataset.productImage || "";
            const productDescription = openEl.dataset.productDescription || "";
            if (productId && typeof window.openProductModal === "function") {
                window.openProductModal(productId, productName, productPrice, productImage, productDescription);
            }
            return;
        }

        const addEl = event.target.closest(".js-add-product");
        if (addEl) {
            const productId = parseInt(addEl.dataset.productId || "0", 10);
            const productName = addEl.dataset.productName || "";
            const productImage = addEl.dataset.productImage || "";
            const productPrice = parseFloat(addEl.dataset.productPrice || "0") || 0;
            if (productId) {
                addProductToCart(productId, productName, productImage, productPrice);
            }
        }
    });

    function buildUrl(page) {
        const params = new URLSearchParams();
        const search = (searchInput?.value || filterState.search || "").trim();
        const category = filterState.category || "all";
        const sort = sortSelect?.value || filterState.sort || "newest";

        params.set("page", String(page || 1));
        if (search) {
            params.set("q", search);
        }
        if (category && category !== "all") {
            params.set("category", category);
        }
        if (sort && sort !== "newest") {
            params.set("sort", sort);
        }
        return `/?${params.toString()}`;
    }

    if (searchForm) {
        searchForm.addEventListener("submit", function (event) {
            event.preventDefault();
            window.location.href = buildUrl(1);
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener("change", function () {
            window.location.href = buildUrl(1);
        });
    }

    categoryButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            event.preventDefault();
            filterState.category = button.dataset.category || "all";
            window.location.href = buildUrl(1);
        });
    });

    paginationButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            if (button.classList.contains("disabled")) {
                return;
            }
            const page = parseInt(button.dataset.page || "1", 10);
            if (Number.isNaN(page) || page < 1 || page > (filterState.totalPages || 1)) {
                return;
            }
            window.location.href = buildUrl(page);
        });
    });

    bestItems.forEach(function (item) {
        item.addEventListener("click", function () {
            const productId = item.dataset.focusProduct;
            if (!productId) {
                return;
            }
            const card = document.getElementById(`product-${productId}`);
            if (card) {
                card.scrollIntoView({ behavior: "smooth", block: "center" });
                card.classList.add("focus-highlight");
                setTimeout(function () {
                    card.classList.remove("focus-highlight");
                }, 1400);
            }
        });
    });
});

function addProductToCart(productId, productName, productImage, productPrice) {
    if (!window.cartClient) {
        alert("Giỏ hàng chưa sẵn sàng. Vui lòng thử lại.");
        return;
    }

    window.cartClient.addToCart(productId, 1, {
        name: productName,
        image: productImage,
        price: productPrice,
    }).then(function (ok) {
        if (ok) {
            alert(`Đã thêm ${productName} vào giỏ hàng.`);
        }
    });
}
