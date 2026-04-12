# BaiTapNhom

## AI chat cho giao dien user

Da them widget chat o `src/templates/user/layout.html` va endpoint proxy Flask o `src/chat.py`.

Kien truc:
- Flask app nhan request tu widget tai `POST /api/chat`.
- Flask proxy goi sang FastAPI chatbot service (`/chat`).
- Chatbot service doc du lieu tu `instance/data.db` de tra loi theo nghiep vu BaiTapNhom.
- Neu da dang nhap, chat su dung `user_id` gan voi tai khoan (`user_<id>`); khach vang lai dung `guest_*`.
- Neu upstream chatbot bi sai endpoint/khong chay, Flask se tu dong fallback sang local `ai_chatbot` de khong bi loi `Not Found`.

### 1) Cai dat dependencies

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python -m pip install -r requirements.txt
```

### 2) Chay chatbot service (FastAPI)

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
uvicorn ai_chatbot.api.main:app --host 127.0.0.1 --port 8001 --reload
```

Bien moi truong tuy chon:
- `GOOGLE_API_KEY`: bat Gemini (neu khong co se fallback rule-based).
- `CHATBOT_MODEL`: mac dinh `gemini-2.0-flash`.
- `INVENSTORY_DB_PATH`: duong dan DB app (mac dinh `instance/data.db`).
- `CHATBOT_SQLITE_DB_PATH`: duong dan luu lich su chat.

### 3) Chay Flask app

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python app.py
```

Neu chatbot service chay khac URL, dat:
- `CHATBOT_API_URL` (mac dinh `http://127.0.0.1:8001/chat`)
- `CHATBOT_TIMEOUT` (giay, mac dinh `30`)

### 4) Smoke test chatbot nhanh

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python -m ai_chatbot.test_chatbot
```

### 5) Neu chat bi "Not Found"

Kiem tra chatbot service:

```zsh
curl http://127.0.0.1:8001/health
```

Kiem tra endpoint chatbot truc tiep:

```zsh
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","chat_session_id":"s1","new_query":"xin chao"}'
```

Kiem tra proxy Flask:

```zsh
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","chat_session_id":"s1","new_query":"xin chao"}'
```

## Seed du lieu demo cho bao cao doanh thu

Script `seed_reports_demo.py` se tao nhieu don hang da thanh toan VNPay cho thang 1 den thang 4 (nam hien tai) de xem bieu do ro hon.

- Du lieu demo dung prefix `RPTDEMO4M-` cho ma don.
- Moi lan chay script se xoa du lieu demo cu va tao lai de tranh trung lap.
- Script khong xoa du lieu don hang that khac.

Chay script:

```zsh
cd "/Users/nguyenngocanh/Downloads/Documents/Kỳ 2 năm 3/SOA/BaiTapNhom"
python seed_reports_demo.py
```

Sau do vao trang `Admin -> Thong ke doanh thu`:

- Chon `Theo nam` de xem bieu do 12 thang.
- Chon `Tuy chinh` de loc theo khoang ngay va gom nhom ngay/tuan/thang.


