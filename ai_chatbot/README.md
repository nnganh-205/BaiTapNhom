# InvenStory AI Chatbot Service

Service FastAPI cung cấp endpoint `POST /chat` cho widget chat ở `BaiTapNhom`.

## Tính năng
- Lưu lịch sử chat theo session vào SQLite (`ai_chatbot/chat_history.db`).
- Grounding theo dữ liệu thực tế từ `instance/data.db` (sản phẩm, giá, tồn kho, top món).
- Trả lời tiếng Việt có dấu, tự nhiên hơn và đa dạng cách diễn đạt.
- Nếu có `GOOGLE_API_KEY`: gọi Gemini để trả lời thông minh hơn.
- Nếu không có key hoặc lỗi model: fallback theo luật, vẫn bám dữ liệu nội bộ.

## Chạy service
```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
uvicorn ai_chatbot.api.main:app --host 127.0.0.1 --port 8001 --reload
```

## Test nhanh
```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python -m ai_chatbot.test_chatbot
```

## Tạo bộ dữ liệu câu hỏi AI (siêu lớn)
Script sinh dữ liệu tổng hợp cho chatbot, bao gồm cả câu thiếu chủ-vị, câu chat ngắn, viết tắt, không dấu:

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python ai_chatbot/scripts/generate_huge_chat_dataset.py --total-samples 200000
```

Tăng quy mô lên 1 triệu câu:

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python ai_chatbot/scripts/generate_huge_chat_dataset.py --total-samples 1000000 --seed 20260414
```

Kết quả mặc định nằm ở `ai_chatbot/data/synthetic/`:
- `train.jsonl`, `dev.jsonl`, `test.jsonl`
- `train.csv`, `dev.csv`, `test.csv`
- `stats.json` (thống kê intent + tỉ lệ câu ngắn)

Schema mỗi dòng:
- `id`: mã mẫu tổng hợp
- `text`: câu người dùng
- `intents`: danh sách intent (có thể đa intent)
- `primary_intent`: intent chính
- `is_fragment`: câu ngắn/thiếu thành phần
- `source`: nguồn dữ liệu (`synthetic_v1`)

## Biến môi trường
- `GOOGLE_API_KEY` (optional)
- `CHATBOT_MODEL` (default: `gemini-2.0-flash`)
- `INVENSTORY_DB_PATH` (default: `instance/data.db`)
- `CHATBOT_SQLITE_DB_PATH` (default: `ai_chatbot/chat_history.db`)

## Cấu hình `.env` (khuyến nghị)
```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
cp ai_chatbot/.env.example ai_chatbot/.env
```

Sau đó mở `ai_chatbot/.env` và điền key thật:

```dotenv
GOOGLE_API_KEY=AIzaSyBmvz0WeKYltQN6QlggRCNS5yd5XKAOI3E
CHATBOT_MODEL=gemini-2.0-flash
```

`BaiTapNhom/.gitignore` đã bỏ qua `.env`, nhưng vẫn nên tránh gửi key qua chat/screenshot.

## Cấu hình Gemini qua shell (tuỳ chọn)
```zsh
export GOOGLE_API_KEY="<API_KEY_CUA_BAN>"
export CHATBOT_MODEL="gemini-2.0-flash"
```

