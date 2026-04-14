from ai_chatbot.chatbot import chat_once


def run_demo() -> None:
    history = [
        {"role": "user", "content": "Xin chao"},
        {"role": "assistant", "content": "Chào bạn, mình có thể hỗ trợ gì?"},
    ]
    demo_queries = [
        "Menu có những món nào?",
        "Món nào đang giảm giá?",
        "Có đồ uống hay tráng miệng không?",
        "Món nào đang còn hàng?",
        "Gợi ý giúp mình combo cho 3 người, ngân sách 180k",
        "Top món bán chạy hiện tại là gì?",
        "Pizza Mini giá bao nhiêu?",
        "Thanh toán VNPay như nào?",
        "Bạn có người yêu chưa?",  # Out-of-scope, kiểm tra trả lời nhí nhảnh
        "Thời tiết hôm nay thế nào?",  # Out-of-scope, kiểm tra trả lời nhí nhảnh
        "Gợi ý combo dưới 200k cho 3 người",  # In-scope, kiểm tra logic cũ
    ]

    for query in demo_queries:
        answer = chat_once("demo_user", "demo_session", query, history)
        print(f"Q: {query}")
        print(f"A: {answer}\n")
        history.append({"role": "user", "content": query})
        history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    run_demo()
