/**
 * main.js - Shared UI and AI chat widget for user pages.
 */

const CHAT_API_URL = "/api/chat";

function getAuthenticatedChatUserId() {
    if (!window.chatIdentity || !window.chatIdentity.isAuthenticated) {
        return "";
    }
    return String(window.chatIdentity.userId || "").trim();
}

function getChatUserId() {
    const authUserId = getAuthenticatedChatUserId();
    if (authUserId) {
        return authUserId;
    }

    const cached = localStorage.getItem("chat_uid");
    if (cached) {
        return `guest_${cached}`;
    }
    const generated = Math.random().toString(36).slice(2, 10);
    localStorage.setItem("chat_uid", generated);
    return `guest_${generated}`;
}

function getChatSessionId(userId) {
    const key = `chat_session_${userId}`;
    const cached = localStorage.getItem(key);
    if (cached) {
        return cached;
    }

    const generated = `sess_${Date.now()}`;
    localStorage.setItem(key, generated);
    return generated;
}

const CHAT_USER_ID = getChatUserId();
const CHAT_SESSION_ID = getChatSessionId(CHAT_USER_ID);
let CHAT_IS_SENDING = false;

function appendMessage(text, role) {
    const box = document.getElementById("chat-messages");
    if (!box) {
        return;
    }

    const wrapper = document.createElement("div");
    wrapper.className = `msg ${role}-msg`;

    const bubble = document.createElement("div");
    bubble.className = "msg-bubble";
    bubble.innerHTML = String(text || "").replace(/\n/g, "<br>");

    wrapper.appendChild(bubble);
    box.appendChild(wrapper);
    box.scrollTop = box.scrollHeight;
}

function showTyping() {
    const box = document.getElementById("chat-messages");
    if (!box) {
        return null;
    }

    const wrapper = document.createElement("div");
    wrapper.className = "msg bot-msg";
    wrapper.innerHTML = '<div class="typing-bubble"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
    box.appendChild(wrapper);
    box.scrollTop = box.scrollHeight;
    return wrapper;
}

function hideTyping(el) {
    if (el) {
        el.remove();
    }
}

function hideSuggestions() {
    const block = document.getElementById("chat-suggestions");
    if (block) {
        block.style.display = "none";
    }
}

function autoResize(el) {
    if (!el) {
        return;
    }
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 96)}px`;
}

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    if (!input || !sendBtn) {
        return;
    }

    const text = input.value.trim();
    if (!text || CHAT_IS_SENDING) {
        return;
    }

    CHAT_IS_SENDING = true;
    appendMessage(text, "user");
    input.value = "";
    autoResize(input);
    hideSuggestions();
    sendBtn.disabled = true;
    const typingEl = showTyping();

    try {
        const response = await fetch(CHAT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_id: CHAT_USER_ID,
                chat_session_id: CHAT_SESSION_ID,
                new_query: text,
            }),
        });

        const data = await response.json();
        hideTyping(typingEl);
        appendMessage(data.answer || data.detail || "Hệ thống tạm thời bận, vui lòng thử lại sau.", "bot");
    } catch (error) {
        hideTyping(typingEl);
        appendMessage("Không thể kết nối chatbot lúc này. Bạn thử lại sau nhé!", "bot");
    } finally {
        CHAT_IS_SENDING = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const mobileToggle = document.getElementById("mobileToggle");
    const navMenu = document.getElementById("navMenu");
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener("click", function() {
            navMenu.classList.toggle("active");
        });
    }

    const chatBubble = document.getElementById("chat-bubble");
    const chatWindow = document.getElementById("chat-window");
    const openIcon = document.getElementById("bubble-icon-open");
    const closeIcon = document.getElementById("bubble-icon-close");
    const closeBtn = document.getElementById("chat-close-btn");
    const input = document.getElementById("chat-input");
    const sendBtn = document.getElementById("send-btn");
    const suggestionButtons = document.querySelectorAll(".suggest-btn");
    let isComposing = false;

    if (chatBubble && chatWindow) {
        const toggleChat = function(forceOpen) {
            const isOpen = typeof forceOpen === "boolean"
                ? forceOpen
                : !chatWindow.classList.contains("open");

            chatWindow.classList.toggle("open", isOpen);
            chatWindow.setAttribute("aria-hidden", String(!isOpen));
            if (openIcon) openIcon.style.display = isOpen ? "none" : "";
            if (closeIcon) closeIcon.style.display = isOpen ? "" : "none";

            if (isOpen && input) {
                setTimeout(() => input.focus(), 120);
            }
        };

        chatBubble.addEventListener("click", () => toggleChat());
        if (closeBtn) {
            closeBtn.addEventListener("click", () => toggleChat(false));
        }
    }

    if (input) {
        input.addEventListener("compositionstart", function() {
            isComposing = true;
        });
        input.addEventListener("compositionend", function() {
            isComposing = false;
        });
        input.addEventListener("input", function() {
            autoResize(input);
        });
        input.addEventListener("keydown", function(event) {
            if (event.key === "Enter" && !event.shiftKey) {
                if (isComposing || event.isComposing || event.keyCode === 229) {
                    return;
                }
                event.preventDefault();
                sendMessage();
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }

    suggestionButtons.forEach((button) => {
        button.addEventListener("click", function() {
            if (!input) {
                return;
            }
            input.value = button.textContent || "";
            autoResize(input);
            sendMessage();
        });
    });

    window.addEventListener("scroll", function() {
        const navbar = document.querySelector(".navbar-client");
        if (!navbar) {
            return;
        }
        if (window.scrollY > 50) {
            navbar.style.padding = "10px 0";
            navbar.style.boxShadow = "0 5px 20px rgba(0,0,0,0.1)";
        } else {
            navbar.style.padding = "15px 0";
            navbar.style.boxShadow = "none";
        }
    });

    const btnAdd = document.getElementById("btnAddProduct");
    if (btnAdd) {
        btnAdd.addEventListener("click", function() {
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