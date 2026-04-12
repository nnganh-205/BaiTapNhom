(function () {
    const GUEST_CART_KEY = "guest_cart_v1";
    let cartState = { items: [], total_amount: 0, total_quantity: 0 };

    function formatCurrency(amount) {
        return `${new Intl.NumberFormat("vi-VN").format(Math.round(amount || 0))}₫`;
    }

    function updateCartUI(cart) {
        cartState = cart || cartState;
        const countEl = document.getElementById("cart-count");
        const totalEl = document.getElementById("sideCartTotal");
        const contentEl = document.getElementById("sideCartContent");

        if (countEl) {
            countEl.innerText = String(cartState.total_quantity || 0);
        }
        if (totalEl) {
            totalEl.innerText = formatCurrency(cartState.total_amount || 0);
        }
        if (!contentEl) {
            return;
        }

        if (!cartState.items || cartState.items.length === 0) {
            contentEl.innerHTML = '<p class="text-muted">Giỏ hàng đang trống.</p>';
            return;
        }

        contentEl.innerHTML = cartState.items
            .map(
                (item) => `
                <div class="side-cart-item" data-cart-item-id="${item.id}">
                    <img src="${item.image_url || "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=400&auto=format&fit=crop"}" alt="${item.product_name}">
                    <div class="item-info">
                        <h4>${item.product_name}</h4>
                        <div class="item-price">${formatCurrency(item.unit_price)}</div>
                        <div class="item-qty">
                            <button type="button" data-action="decrease">-</button>
                            <span>${item.quantity}</span>
                            <button type="button" data-action="increase">+</button>
                        </div>
                    </div>
                    <button class="del-item" type="button" data-action="remove"><i class="fa-solid fa-trash-can"></i></button>
                </div>`
            )
            .join("");
    }

    function loadGuestCart() {
        try {
            const raw = localStorage.getItem(GUEST_CART_KEY);
            if (!raw) {
                return { items: [], total_amount: 0, total_quantity: 0 };
            }
            const parsed = JSON.parse(raw);
            return {
                items: Array.isArray(parsed.items) ? parsed.items : [],
                total_amount: Number(parsed.total_amount || 0),
                total_quantity: Number(parsed.total_quantity || 0),
            };
        } catch (error) {
            return { items: [], total_amount: 0, total_quantity: 0 };
        }
    }

    function saveGuestCart(cart) {
        localStorage.setItem(GUEST_CART_KEY, JSON.stringify(cart));
    }

    function clearGuestCart() {
        localStorage.removeItem(GUEST_CART_KEY);
    }

    function upsertGuestItem(productId, quantity, meta) {
        const cart = loadGuestCart();
        const existing = cart.items.find((item) => Number(item.product_id) === Number(productId));

        if (existing) {
            existing.quantity += quantity;
            existing.line_total = existing.quantity * existing.unit_price;
        } else {
            const unitPrice = Number(meta?.price || 0);
            cart.items.push({
                id: `guest-${productId}`,
                product_id: productId,
                product_name: meta?.name || "Sản phẩm",
                image_url: meta?.image || "",
                quantity,
                unit_price: unitPrice,
                line_total: unitPrice * quantity,
            });
        }

        cart.total_quantity = cart.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
        cart.total_amount = cart.items.reduce((sum, item) => sum + (Number(item.quantity || 0) * Number(item.unit_price || 0)), 0);
        saveGuestCart(cart);
        updateCartUI(cart);
    }

    function changeGuestItemQuantity(itemId, quantity) {
        const cart = loadGuestCart();
        const target = cart.items.find((item) => String(item.id) === String(itemId));
        if (!target) {
            return;
        }

        if (quantity <= 0) {
            cart.items = cart.items.filter((item) => String(item.id) !== String(itemId));
        } else {
            target.quantity = quantity;
            target.line_total = target.quantity * target.unit_price;
        }

        cart.total_quantity = cart.items.reduce((sum, item) => sum + Number(item.quantity || 0), 0);
        cart.total_amount = cart.items.reduce((sum, item) => sum + (Number(item.quantity || 0) * Number(item.unit_price || 0)), 0);
        saveGuestCart(cart);
        updateCartUI(cart);
    }

    async function syncGuestCartToServer() {
        const guestCart = loadGuestCart();
        if (!guestCart.items.length) {
            return;
        }

        for (const item of guestCart.items) {
            await fetch("/api/v1/cart/items", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ product_id: item.product_id, quantity: item.quantity }),
            });
        }

        clearGuestCart();
    }

    function handleUnauthorized() {
        alert("Bạn cần đăng nhập để thanh toán.");
        window.location.href = "/auth/login?next=/checkout";
    }

    async function fetchCart() {
        if (!window.isAuthenticated) {
            updateCartUI(loadGuestCart());
            return;
        }

        await syncGuestCartToServer();
        const res = await fetch("/api/v1/cart");
        if (res.status === 401) {
            return;
        }
        const data = await res.json();
        updateCartUI(data);
    }

    async function addToCart(productId, quantity, meta) {
        if (!window.isAuthenticated) {
            upsertGuestItem(productId, quantity || 1, meta || {});
            return true;
        }

        const res = await fetch("/api/v1/cart/items", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ product_id: productId, quantity: quantity || 1 }),
        });

        if (res.status === 401) {
            handleUnauthorized();
            return false;
        }
        if (!res.ok) {
            const data = await res.json().catch(() => ({}));
            alert(data.message || "Không thể thêm vào giỏ hàng.");
            return false;
        }

        updateCartUI(await res.json());
        return true;
    }

    async function changeItemQuantity(itemId, quantity) {
        if (!window.isAuthenticated) {
            changeGuestItemQuantity(itemId, quantity);
            return;
        }

        const res = await fetch(`/api/v1/cart/items/${itemId}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ quantity }),
        });
        if (!res.ok) {
            return;
        }
        updateCartUI(await res.json());
    }

    async function removeItem(itemId) {
        if (!window.isAuthenticated) {
            changeGuestItemQuantity(itemId, 0);
            return;
        }

        const res = await fetch(`/api/v1/cart/items/${itemId}`, { method: "DELETE" });
        if (!res.ok) {
            return;
        }
        updateCartUI(await res.json());
    }

    document.addEventListener("click", async function (event) {
        const itemEl = event.target.closest(".side-cart-item[data-cart-item-id]");
        if (!itemEl) {
            return;
        }

        const actionEl = event.target.closest("[data-action]");
        if (!actionEl) {
            return;
        }

        const itemId = parseInt(itemEl.dataset.cartItemId || "0", 10);
        const quantityText = itemEl.querySelector(".item-qty span")?.innerText || "1";
        const currentQty = parseInt(quantityText, 10) || 1;

        if (actionEl.dataset.action === "increase") {
            await changeItemQuantity(itemId, currentQty + 1);
        }
        if (actionEl.dataset.action === "decrease") {
            await changeItemQuantity(itemId, currentQty - 1);
        }
        if (actionEl.dataset.action === "remove") {
            await removeItem(itemId);
        }
    });

    const checkoutBtn = document.querySelector(".btn-checkout");
    if (checkoutBtn) {
        checkoutBtn.addEventListener("click", function () {
            if (!window.isAuthenticated) {
                handleUnauthorized();
                return;
            }

            if (!cartState.items || cartState.items.length === 0) {
                alert("Giỏ hàng đang trống.");
                return;
            }
            window.location.href = "/checkout";
        });
    }

    window.cartClient = {
        fetchCart,
        addToCart,
        updateCartUI,
    };

    fetchCart();
})();




