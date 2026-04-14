import os
import re
import sqlite3
import unicodedata
import random
from typing import Any, Dict, List, Set, Optional

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

from ai_chatbot.llms.gemini import LLM

load_dotenv()

# Custom State bao gồm messages từ MessagesState + custom context
class State(MessagesState):
    context: List[str]


def _default_app_db_path() -> str:
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "instance", "data.db")


APP_DB_PATH = os.getenv("INVENSTORY_DB_PATH", _default_app_db_path())
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("CHATBOT_MODEL", "gemini-2.0-flash")
ALLOWED_TOPICS = {
    "menu",
    "thuc don",
    "mon an",
    "san pham",
    "gia",
    "khuyen mai",
    "ton kho",
    "dat hang",
    "giao hang",
    "thanh toan",
    "vnpay",
    "combo",
    "khau vi",
    "an kieng",
    "uu dai",
}

STOPWORDS = {
    "la",
    "va",
    "voi",
    "cho",
    "nhe",
    "nha",
    "minh",
    "toi",
    "ban",
    "giup",
    "duoc",
    "co",
    "cua",
    "nhung",
    "mon",
    "san",
    "pham",
    "nao",
    "bao",
    "nhieu",
    "gia",
    "goi",
    "y",
}

INTENT_KEYWORDS = {
    "greeting": {"xin chao", "chao", "hello", "hi", "alo"},
    "menu": {"menu", "thuc don", "co mon gi", "ban mon gi", "goi y mon", "do an", "nuoc uong", "trang mieng"},
    "budget": {"ngan sach", "duoi", "toi da", "bao nhieu", "goi y", "combo", "an gi", "hop"},
    "popular": {"ban chay", "top", "pho bien", "nhieu nguoi goi"},
    "payment": {"vnpay", "thanh toan", "payment", "checkout"},
    "availability": {"con hang", "ton kho", "available", "san pham nao", "mon nao"},
    "diet": {"cay", "it beo", "an kieng", "healthy", "nhat", "nhe bung"},
    "delivery": {"giao hang", "ship", "bao lau", "freeship", "van chuyen"},
    "promotion": {"khuyen mai", "uu dai", "giam gia", "voucher", "deal"},
    "order": {"dat hang", "mua", "goi mon", "order"},
}

AFFIRMATIVE_REPLIES = {
    "co",
    "co nhe",
    "co nha",
    "ok",
    "oke",
    "yes",
    "dong y",
    "them di",
    "them nhe",
}

NEGATIVE_REPLIES = {
    "khong",
    "khong nhe",
    "khong can",
    "thoi",
    "no",
    "bo qua",
}


def _query_rows(query: str, params: tuple = ()) -> List[sqlite3.Row]:
    if not os.path.exists(APP_DB_PATH):
        return []

    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(query, params).fetchall()
    finally:
        conn.close()


def _format_currency(value: float) -> str:
    return f"{value:,.0f} VND".replace(",", ".")


def _normalize_text(text: str) -> str:
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text.replace("đ", "d")


def _tokenize(text: str) -> Set[str]:
    normalized = _normalize_text(text)
    tokens = re.findall(r"[a-z0-9]+", normalized)
    return {token for token in tokens if len(token) > 1 and token not in STOPWORDS}


def _detect_intents(query: str) -> Set[str]:
    lowered = _normalize_text(query)
    tokens = set(re.findall(r"[a-z0-9]+", lowered))
    intents = set()
    for intent, keywords in INTENT_KEYWORDS.items():
        normalized_keywords = {_normalize_text(keyword) for keyword in keywords}
        if any((keyword in lowered) if " " in keyword else (keyword in tokens) for keyword in normalized_keywords):
            intents.add(intent)
    if _extract_budget_vnd(query) > 0:
        intents.add("budget")
    return intents


def get_domain_context() -> Dict[str, List[Dict[str, str]]]:
    products = _query_rows(
        """
        SELECT p.id, p.name, p.description, p.is_available,
               c.name AS category_name,
               COALESCE(MIN(v.price), 0) AS min_original_price,
               COALESCE(MIN(v.price * (1 - COALESCE(v.discount_percent, 0) / 100.0)), 0) AS min_sale_price,
               COALESCE(MAX(v.discount_percent), 0) AS max_discount_percent,
               COALESCE(SUM(v.stock), 0) AS total_stock
        FROM products p
        LEFT JOIN categories c ON c.id = p.category_id
        LEFT JOIN product_variants v ON v.product_id = p.id
        GROUP BY p.id, p.name, p.description, p.is_available, c.name
        ORDER BY p.created_at DESC
        LIMIT 30
        """
    )

    top_products = _query_rows(
        """
        SELECT p.name, SUM(oi.quantity) AS sold_qty
        FROM order_items oi
        JOIN products p ON p.id = oi.product_id
        JOIN orders o ON o.id = oi.order_id
        WHERE o.status != 'cancelled'
        GROUP BY p.id, p.name
        ORDER BY sold_qty DESC
        LIMIT 5
        """
    )

    mapped_products: List[Dict[str, str]] = []
    for row in products:
        max_discount = float(row["max_discount_percent"] or 0)
        original_price = float(row["min_original_price"] or 0)
        sale_price = float(row["min_sale_price"] or original_price)
        display_price = sale_price if max_discount > 0 else original_price
        mapped_products.append(
            {
                "name": row["name"],
                "category": row["category_name"] or "Khac",
                "price": _format_currency(display_price),
                "price_original": _format_currency(original_price),
                "price_sale": _format_currency(sale_price),
                "discount_percent": max_discount,
                "stock": str(int(row["total_stock"] or 0)),
                "status": "con hang" if int(row["is_available"] or 0) and int(row["total_stock"] or 0) > 0 else "tam het",
                "description": (row["description"] or "").strip()[:180],
            }
        )

    mapped_top = [{"name": row["name"], "sold_qty": str(int(row["sold_qty"] or 0))} for row in top_products]
    return {"products": mapped_products, "top_products": mapped_top}


def _score_product_relevance(product: Dict[str, str], query_tokens: Set[str]) -> int:
    if not query_tokens:
        return 0
    # So khớp các trường chính của sản phẩm
    fields = [product.get("name", ""), product.get("description", ""), product.get("category", "")]
    score = 0
    for field in fields:
        field_tokens = _tokenize(field)
        overlap = len(field_tokens & query_tokens)
        score += overlap * (3 if field == product.get("name", "") else 1)
    return score


def _select_relevant_products(context: Dict[str, List[Dict[str, str]]], query: str) -> List[Dict[str, str]]:
    products = context["products"]
    if not products:
        return []

    query_tokens = _tokenize(query)
    intents = _detect_intents(query)
    budget = _extract_budget_vnd(query)

    scored = []
    for product in products:
        score = _score_product_relevance(product, query_tokens)
        if product["status"] == "con hang":
            score += 1
        if "budget" in intents and budget > 0:
            price_value = _price_to_number(product["price"])
            if 0 < price_value <= budget:
                score += 3
        scored.append((score, product))

    best = [item for score, item in sorted(scored, key=lambda x: x[0], reverse=True) if score > 0]
    if best:
        return best[:10]

    if "popular" in intents and context["top_products"]:
        popular_names = {_normalize_text(item["name"]) for item in context["top_products"]}
        popular_products = [p for p in products if _normalize_text(p["name"]) in popular_names]
        if popular_products:
            return popular_products[:10]

    return products[:8]


def _build_recent_history_text(history: List[Dict[str, str]]) -> str:
    snippets = []
    for item in history[-6:]:
        role = "Khach" if item.get("role") == "user" else "Tro ly"
        content = (item.get("content") or "").strip()
        if content:
            snippets.append(f"- {role}: {content[:180]}")
    return "\n".join(snippets)


def _build_context_text(context: Dict[str, List[Dict[str, str]]], query: str, history: List[Dict[str, str]]) -> str:
    relevant_products = _select_relevant_products(context, query)
    lines = ["San pham lien quan nhat:"]
    for product in relevant_products:
        lines.append(
            "- {name} | Nhóm: {category} | Giá từ: {price} | Tồn: {stock} | Trạng thái: {status} | Mô tả: {description}".format(
                **product
            )
        )

    if context["top_products"]:
        lines.append("\nTop món được đặt nhiều:")
        for item in context["top_products"]:
            lines.append(f"- {item['name']}: {item['sold_qty']} lượt")

    history_text = _build_recent_history_text(history)
    if history_text:
        lines.append("\nHoi thoai gan day:")
        lines.append(history_text)

    return "\n".join(lines)


def _price_to_number(price_text: str) -> int:
    digits = re.sub(r"[^0-9]", "", str(price_text or ""))
    return int(digits) if digits else 0


def _extract_budget_vnd(query: str) -> int:
    text = _normalize_text(query).replace(",", ".")
    patterns = [
        r"(\d+[\d\.]*)\s*(trieu|tr|m|mio)",
        r"(\d+[\d\.]*)\s*(nghin|ngan|k)",
        r"(\d+[\d\.]*)\s*(vnd|dong)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        raw = match.group(1).replace(".", "")
        if not raw.isdigit():
            continue
        value = int(raw)
        unit = match.group(2)
        if unit in {"trieu", "tr", "m", "mio"}:
            return value * 1_000_000
        if unit in {"nghin", "ngan", "k"}:
            return value * 1_000
        return value

    plain_number = re.search(r"\b(\d{4,9})\b", text)
    if plain_number:
        return int(plain_number.group(1))
    return 0


def _extract_people_count(query: str) -> int:
    text = _normalize_text(query)
    match = re.search(r"(\d+)\s*(nguoi|ng)", text)
    if not match:
        return 0
    return max(1, int(match.group(1)))


def _is_short_followup(query: str, candidates: Set[str]) -> bool:
    normalized = _normalize_text(query)
    if normalized in candidates:
        return True
    return len(re.findall(r"[a-z0-9]+", normalized)) <= 2 and normalized in candidates


def _get_last_assistant_message(history: List[Dict[str, str]]) -> str:
    for item in reversed(history):
        if item.get("role") == "assistant":
            return (item.get("content") or "").strip()
    return ""


def _get_previous_user_message(history: List[Dict[str, str]], current_query: str) -> str:
    normalized_current = _normalize_text(current_query)
    skipped_current = False
    for item in reversed(history):
        if item.get("role") != "user":
            continue
        content = (item.get("content") or "").strip()
        if not content:
            continue
        normalized = _normalize_text(content)
        if not skipped_current and normalized == normalized_current:
            skipped_current = True
            continue
        return content
    return ""


def _get_recent_user_messages(history: List[Dict[str, str]], limit: int = 4) -> List[str]:
    messages: List[str] = []
    for item in reversed(history):
        if item.get("role") != "user":
            continue
        content = (item.get("content") or "").strip()
        if not content:
            continue
        messages.append(content)
        if len(messages) >= limit:
            break
    messages.reverse()
    return messages


def _is_contextual_followup(query: str) -> bool:
    normalized = _normalize_text(query)
    tokens = re.findall(r"[a-z0-9]+", normalized)
    if len(tokens) <= 6 and _extract_people_count(query) > 0:
        return True
    return any(phrase in normalized for phrase in ["nguoi an", "an thoi", "mot minh", "1 minh"])


def _enrich_query_from_history(query: str, history: List[Dict[str, str]]) -> str:
    if not _is_contextual_followup(query):
        return query

    previous_user = _get_previous_user_message(history, query)
    if not previous_user:
        return query

    previous_budget = _extract_budget_vnd(previous_user)
    current_budget = _extract_budget_vnd(query)
    previous_intents = _detect_intents(previous_user)
    current_intents = _detect_intents(query)

    should_enrich = (
        previous_budget > 0
        or bool(previous_intents & {"budget", "menu", "availability", "popular", "diet", "order"})
    ) and len(current_intents) <= 1

    if not should_enrich:
        return query

    suffix = query if current_budget > 0 else f"{query} ngan sach {previous_budget}" if previous_budget > 0 else query
    return f"{previous_user}. {suffix}".strip()


def _extract_conversation_constraints(query: str, history: List[Dict[str, str]]) -> Dict[str, int]:
    budget = _extract_budget_vnd(query)
    people = _extract_people_count(query)

    if budget > 0 and people > 0:
        return {"budget": budget, "people": people}

    for content in reversed(_get_recent_user_messages(history, limit=8)):
        if budget <= 0:
            previous_budget = _extract_budget_vnd(content)
            if previous_budget > 0:
                budget = previous_budget
        if people <= 0:
            previous_people = _extract_people_count(content)
            if previous_people > 0:
                people = previous_people
        if budget > 0 and people > 0:
            break

    return {"budget": budget, "people": people}


def _is_dessert_query(query: str) -> bool:
    normalized = _normalize_text(query)
    return any(keyword in normalized for keyword in ["trang mieng", "dessert", "banh ngot", "pudding", "flan", "lava"])


def _is_drink_query(query: str) -> bool:
    normalized = _normalize_text(query)
    return any(keyword in normalized for keyword in ["do uong", "nuoc", "tra", "coffee", "drink", "uong gi"])


def _build_addon_recommendation(
    query: str,
    products: List[Dict[str, str]],
    bucket: str,
    bucket_label: str,
    budget: int,
    people: int,
    repeated_count: int,
) -> str:
    candidates = []
    for item in products:
        if item["status"] != "con hang":
            continue
        if _category_bucket(item["category"], item["name"]) != bucket:
            continue
        price_value = _price_to_number(item["price"])
        if price_value <= 0:
            continue
        candidates.append({**item, "price_value": price_value})

    if not candidates:
        return ""

    query_tokens = _tokenize(query)
    ranked = sorted(
        candidates,
        key=lambda x: (_score_product_relevance(x, query_tokens), -x["price_value"]),
        reverse=True,
    )

    if not ranked:
        return ""

    picks = ", ".join(f"{x['name']} ({x['price']})" for x in ranked[:3])
    return _pick_variant(
        f"{query}-addon-{bucket}-{repeated_count}",
        [
            f"Nếu bạn muốn thêm {bucket_label}, mình gợi ý: {picks}.",
            f"Bạn có thể ghép thêm {bucket_label} như: {picks}.",
            f"Để combo đầy đủ hơn, thử {bucket_label}: {picks}.",
        ],
    )


def _fuzzy_token_score(query_tokens: Set[str], candidate_tokens: Set[str]) -> int:
    score = 0
    for query_token in query_tokens:
        for candidate_token in candidate_tokens:
            if query_token == candidate_token:
                score += 3
                break
            if len(query_token) >= 4 and len(candidate_token) >= 4:
                if query_token.startswith(candidate_token) or candidate_token.startswith(query_token):
                    score += 2
                    break
    return score


def _find_best_product_match(query: str, products: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    normalized_query = _normalize_text(query)
    query_tokens = _tokenize(query)
    if not products or not query_tokens:
        return None

    best_product = None
    best_score = 0

    for product in products:
        product_name = product.get("name", "")
        normalized_name = _normalize_text(product_name)
        if normalized_name and normalized_name in normalized_query:
            return product

        name_tokens = _tokenize(product_name)
        score = _fuzzy_token_score(query_tokens, name_tokens)
        if score > best_score:
            best_score = score
            best_product = product

    # Require stronger evidence to avoid mapping generic words like "pizza" to a wrong item.
    return best_product if best_score >= 4 else None


def _is_product_availability_probe(query: str) -> bool:
    normalized = _normalize_text(query)
    return any(
        phrase in normalized
        for phrase in ["co khong", "khong co", "dau roi", "sao khong thay", "het khong", "con khong"]
    )


def _build_product_specific_reply(query: str, product: Dict[str, str], products: List[Dict[str, str]]) -> str:
    if _is_product_availability_probe(query):
        if product["status"] == "con hang":
            return (
                f"Có nhé, {product['name']} vẫn đang còn hàng. Giá từ {product['price']}, "
                f"thuộc nhóm {product['category']}."
            )

        alternatives = [
            item
            for item in products
            if item["status"] == "con hang" and item["category"] == product["category"] and item["name"] != product["name"]
        ]
        picks = ", ".join(f"{item['name']} ({item['price']})" for item in alternatives[:3])
        if picks:
            return (
                f"{product['name']} hiện tạm hết hàng. Bạn có thể đổi sang: {picks}."
            )
        return f"{product['name']} hiện tạm hết hàng. Mình có thể gợi ý nhóm món khác cùng tầm giá nếu bạn muốn."

    return (
        f"{product['name']} thuộc nhóm {product['category']}, giá từ {product['price']}, "
        f"trạng thái {product['status']}. {product['description']}"
    )


def _extract_requested_product_label(query: str) -> str:
    noise = {
        "co",
        "khong",
        "dau",
        "roi",
        "sao",
        "thay",
        "menu",
        "quan",
        "mon",
        "gi",
        "the",
        "a",
        "ha",
        "nhe",
        "nha",
    }
    tokens = [token for token in re.findall(r"[a-z0-9]+", _normalize_text(query)) if token not in noise]
    if not tokens:
        return "món này"
    return " ".join(tokens[:4])


def _suggest_products_by_query(query: str, products: List[Dict[str, str]]) -> List[Dict[str, str]]:
    normalized = _normalize_text(query)
    keyword_groups = ["pizza", "burger", "ga", "pasta", "trang mieng", "nuoc", "tra"]
    target_keyword = next((keyword for keyword in keyword_groups if keyword in normalized), "")

    if target_keyword:
        filtered = [
            item
            for item in products
            if target_keyword in _normalize_text(item["name"]) or target_keyword in _normalize_text(item["category"])
        ]
    else:
        query_tokens = _tokenize(query)
        filtered = [item for item in products if _fuzzy_token_score(query_tokens, _tokenize(item["name"])) > 0]

    available_first = [item for item in filtered if item["status"] == "con hang"]
    return (available_first or filtered)[:3]


def _get_discounted_products(products: List[Dict[str, str]], only_available: bool = True, limit: int = 6) -> List[Dict[str, str]]:
    discounted = []
    for item in products:
        discount_percent = float(item.get("discount_percent") or 0)
        if discount_percent <= 0:
            continue
        if only_available and item.get("status") != "con hang":
            continue
        discounted.append(item)

    discounted.sort(
        key=lambda x: (float(x.get("discount_percent") or 0), -_price_to_number(x.get("price_sale") or x.get("price"))),
        reverse=True,
    )
    return discounted[:limit]


def _build_budget_recommendation(query: str, available: List[Dict[str, str]], budget: int, people: int, repeated_count: int) -> str:
    query_tokens = _tokenize(query)
    target_per_person = budget // people if people > 0 else budget
    target = max(target_per_person, 1)
    preferences = _extract_budget_preferences(query)

    mains = [item for item in available if _category_bucket(item["category"], item["name"]) == "main"]
    desserts = [item for item in available if _category_bucket(item["category"], item["name"]) == "dessert"]

    if preferences["wants_dessert"] and mains and desserts:
        main_qty = max(1, people // 2) if people > 0 else 1
        dessert_qty = max(1, people // 3) if people > 0 else 1
        combos = []

        sorted_mains = sorted(
            mains,
            key=lambda x: (_score_product_relevance(x, query_tokens), -abs(x["price_value"] - target)),
            reverse=True,
        )[:8]
        sorted_desserts = sorted(
            desserts,
            key=lambda x: (_score_product_relevance(x, query_tokens), -x["price_value"]),
            reverse=True,
        )[:8]

        for main in sorted_mains:
            for dessert in sorted_desserts:
                total = main["price_value"] * main_qty + dessert["price_value"] * dessert_qty
                if total > budget:
                    continue
                score = (
                    _score_product_relevance(main, query_tokens) * 2
                    + _score_product_relevance(dessert, query_tokens) * 2
                    + max(0, (budget - total) // 10000)
                )
                combos.append((score, total, main, dessert))

        combos.sort(key=lambda item: (item[0], item[1]), reverse=True)
        if combos:
            top = combos[:2]
            lines = []
            for index, (_, total, main, dessert) in enumerate(top, start=1):
                lines.append(
                    f"Phương án {index}: {main['name']} x{main_qty} + {dessert['name']} x{dessert_qty} "
                    f"(~{_format_currency(total)})."
                )
            combo_text = " ".join(lines)
            return _pick_variant(
                f"{query}-budget-{repeated_count}",
                [
                    (
                        f"Nếu bạn muốn có cả món chính và tráng miệng trong {_format_currency(budget)}: {combo_text} "
                        "Mình ưu tiên món còn hàng và giá vừa ngân sách."
                    ),
                    (
                        f"Mình ghép combo theo nhu cầu 'đồ ăn + tráng miệng' với ngân sách {_format_currency(budget)}: {combo_text}"
                    ),
                    (
                        f"Để ăn hợp lý trong {_format_currency(budget)}, bạn có thể đi theo combo sau: {combo_text} "
                        "Bạn muốn mình thêm đồ uống vào phương án rẻ nhất không?"
                    ),
                ],
            )

    ranked = []
    for item in available:
        price_value = int(item["price_value"])
        score = 0
        if price_value <= int(target * 1.25):
            score += 10
        elif price_value <= int(target * 1.6):
            score += 5

        # Prioritize dishes that semantically match user query.
        score += _score_product_relevance(item, query_tokens)

        price_gap = abs(price_value - target)
        score -= price_gap // 5000
        ranked.append((score, item))

    ranked.sort(key=lambda x: (x[0], x[1]["price_value"]), reverse=True)
    primary = [item for _, item in ranked[:4]]
    economy = sorted(available, key=lambda x: x["price_value"])[:3]

    if not primary:
        return ""

    primary_text = ", ".join(f"{x['name']} ({x['price']})" for x in primary[:3])
    economy_text = ", ".join(f"{x['name']} ({x['price']})" for x in economy)

    if people > 0:
        estimated_share = max(1, people // 2)
        est_total = sum(x["price_value"] for x in primary[:2]) * estimated_share
        return _pick_variant(
            f"{query}-budget-{repeated_count}",
            [
                (
                    f"Với ngân sách {_format_currency(budget)} cho {people} người (~{_format_currency(target_per_person)}/người), "
                    f"mình đề xuất nhóm món hợp tầm giá: {primary_text}. "
                    f"Nếu muốn tiết kiệm hơn, bạn có thể ưu tiên: {economy_text}."
                ),
                (
                    f"Mình tính nhanh theo mức {_format_currency(target_per_person)}/người: {primary_text}. "
                    f"Cách gọi cân bằng: mỗi món khoảng {estimated_share} phần, tổng tạm tính ~{_format_currency(est_total)}."
                ),
                (
                    f"Để ăn ổn trong {_format_currency(budget)} cho {people} người, bạn có thể chọn: {primary_text}. "
                    f"Phương án an toàn về chi phí: bắt đầu từ {economy_text}, rồi tăng thêm món nếu còn ngân sách."
                ),
            ],
        )

    return _pick_variant(
        f"{query}-budget-{repeated_count}",
        [
            (
                f"Với ngân sách {_format_currency(budget)}, bạn có thể cân nhắc: {primary_text}. "
                f"Nếu muốn tối ưu chi phí: {economy_text}."
            ),
            (
                f"Mức giá này phù hợp để chọn 2-3 món trong nhóm: {primary_text}. "
                "Bạn cho mình thêm số người ăn để mình chốt combo sát hơn nhé."
            ),
        ],
    )


def _handle_followup_confirmation(query: str, products: List[Dict[str, str]], history: List[Dict[str, str]]) -> str:
    last_assistant = _normalize_text(_get_last_assistant_message(history))
    prev_user = _normalize_text(_get_previous_user_message(history, query))
    if not last_assistant:
        return ""

    asked_about_drink = any(
        phrase in last_assistant
        for phrase in ["them do uong", "do uong", "uong vao", "ban muon minh them"]
    )
    asked_about_drink = asked_about_drink or any(
        keyword in prev_user for keyword in ["uong", "do uong", "nuoc", "tra"]
    )

    if _is_short_followup(query, AFFIRMATIVE_REPLIES) and asked_about_drink:
        drinks = []
        for item in products:
            if item["status"] != "con hang":
                continue
            if _category_bucket(item["category"], item["name"]) != "drink":
                continue
            price_value = _price_to_number(item["price"])
            if price_value <= 0:
                continue
            drinks.append({**item, "price_value": price_value})

        if not drinks:
            return "Được nhé. Hiện chưa có đồ uống khả dụng trong dữ liệu, bạn có thể chốt theo combo trước đó."

        drinks = sorted(drinks, key=lambda x: x["price_value"])
        picks = ", ".join(f"{x['name']} ({x['price']})" for x in drinks[:3])
        return _pick_variant(
            f"{query}-drink-followup-{len(history)}",
            [
                f"Ok luôn. Mình gợi ý thêm đồ uống giá mềm để ghép combo: {picks}.",
                f"Có nhé. Bạn có thể thêm một trong các món uống sau: {picks}.",
                f"Hợp lý nè. Đồ uống dễ ghép nhất hiện tại là: {picks}.",
            ],
        )

    if _is_short_followup(query, NEGATIVE_REPLIES) and asked_about_drink:
        return "Ok bạn, vậy mình giữ nguyên combo món ăn + tráng miệng như phương án trước nhé."

    return ""


def _fallback_answer(query: str, context: Dict[str, List[Dict[str, str]]], history: List[Dict[str, str]]) -> str:
    resolved_query = _enrich_query_from_history(query, history)
    lowered = _normalize_text(resolved_query)
    products = context["products"]
    intents = _detect_intents(resolved_query)
    repeated_count = sum(
        1
        for item in history
        if item.get("role") == "user" and _normalize_text(item.get("content", "")) == lowered
    )

    constraints = _extract_conversation_constraints(query, history)
    budget = _extract_budget_vnd(resolved_query) or constraints["budget"]
    people = _extract_people_count(query) or _extract_people_count(resolved_query) or constraints["people"]
    has_budget_intent = "budget" in intents or (budget > 0 and _is_contextual_followup(query))

    if "greeting" in intents:
        return _pick_variant(
            f"{query}-{repeated_count}",
            [
                "Chào bạn, mình có thể tư vấn món theo ngân sách, khẩu vị hoặc số người ăn. Bạn muốn bắt đầu từ đâu?",
                "Xin chào, bạn cần mình gợi ý món bán chạy, món đang còn hàng hay combo theo ngân sách?",
                "Hey bạn, cứ nói nhu cầu như '4 người dưới 200k' hoặc tên món, mình sẽ gợi ý nhanh nhé.",
            ],
        )

    followup_answer = _handle_followup_confirmation(query, products, history)
    if followup_answer:
        return followup_answer

    matched_product = _find_best_product_match(query, products) or _find_best_product_match(resolved_query, products)
    if matched_product:
        return _build_product_specific_reply(query, matched_product, products)

    if _is_product_availability_probe(query):
        requested_label = _extract_requested_product_label(query)
        suggestions = _suggest_products_by_query(query, products)
        if suggestions:
            picks = ", ".join(f"{item['name']} ({item['price']})" for item in suggestions)
            return (
                f"Mình chưa thấy đúng món '{requested_label}' trong dữ liệu hiện tại. "
                f"Bạn có thể tham khảo: {picks}."
            )

    if _is_short_followup(query, AFFIRMATIVE_REPLIES | NEGATIVE_REPLIES):
        return _pick_variant(
            f"{query}-short-followup-{repeated_count}",
            [
                "Mình nhận được phản hồi của bạn rồi. Bạn muốn mình tiếp tục theo hướng nào: thêm đồ uống, lọc món theo ngân sách, hay chốt món đang còn hàng?",
                "Ok bạn. Để mình tư vấn đúng ý hơn, bạn chọn 1 hướng nhé: combo theo ngân sách, món bán chạy, hoặc món còn hàng.",
                "Rõ rồi nè. Bạn cho mình thêm 1 ý chính (ngân sách/số người/khẩu vị), mình đề xuất ngay 2-4 món cụ thể.",
            ],
        )

    if not _is_in_domain(resolved_query, context):
        # If conversation has recent in-domain turns, keep guiding user instead of hard out-of-scope.
        recent_user = " ".join(_get_recent_user_messages(history, limit=3))
        if _is_in_domain(recent_user, context):
            return _pick_variant(
                f"{query}-context-clarify-{repeated_count}",
                [
                    "Mình vẫn đang theo mạch tư vấn trước đó. Bạn cho mình thêm ngân sách hoặc món chính muốn ăn để mình chốt lại combo ngay.",
                    "Mình hiểu bạn đang tiếp nối câu trước. Bạn cần mình ưu tiên burger, đồ uống hay tráng miệng để mình đề xuất sát hơn?",
                    "Để tư vấn liền mạch, bạn cho mình 1 ý chính nữa (ngân sách hoặc khẩu vị), mình sẽ chốt 2-4 lựa chọn cụ thể.",
                ],
            )
        return _build_out_of_scope_reply(query)

    if has_budget_intent and budget > 0:
        available = []
        for item in products:
            if item["status"] != "con hang":
                continue
            price_value = _price_to_number(item["price"])
            if price_value <= 0:
                continue
            available.append({**item, "price_value": price_value})

        if available:
            return _build_budget_recommendation(resolved_query, available, budget, people, repeated_count)

    if has_budget_intent and budget <= 0:
        return (
            "Mình có thể lên combo rất sát nhu cầu. Bạn cho mình 2 thông tin: số người ăn và ngân sách (ví dụ: 4 người dưới 220k)."
        )

    if _is_dessert_query(query):
        dessert_answer = _build_addon_recommendation(
            resolved_query,
            products,
            bucket="dessert",
            bucket_label="món tráng miệng",
            budget=budget,
            people=people,
            repeated_count=repeated_count,
        )
        if dessert_answer:
            return dessert_answer

    if _is_drink_query(query):
        drink_answer = _build_addon_recommendation(
            resolved_query,
            products,
            bucket="drink",
            bucket_label="đồ uống",
            budget=budget,
            people=people,
            repeated_count=repeated_count,
        )
        if drink_answer:
            return drink_answer

    if "menu" in intents:
        available = [p for p in products if p["status"] == "con hang"]
        target = available if available else products
        if not target:
            return "Hiện tại mình chưa tải được dữ liệu menu. Bạn thử lại sau ít phút nhé."

        category_buckets: Dict[str, List[Dict[str, str]]] = {}
        for item in target:
            category_buckets.setdefault(item["category"], []).append(item)

        lines = []
        for category, items in list(category_buckets.items())[:4]:
            picks = ", ".join(f"{x['name']} ({x['price']})" for x in items[:3])
            lines.append(f"- {category}: {picks}")

        menu_text = "\n".join(lines)
        discounted = _get_discounted_products(target, only_available=True, limit=4)
        discount_text = ""
        if discounted:
            discount_lines = "\n".join(
                f"- {item['name']}: {item['price_original']} -> {item['price_sale']} (-{int(float(item['discount_percent']))}%)"
                for item in discounted
            )
            discount_text = f"\nMón đang giảm giá:\n{discount_lines}"
        return (
            "Menu hiện có của InvenStory (rút gọn theo nhóm):\n"
            f"{menu_text}"
            f"{discount_text}\n"
            "Bạn muốn mình lọc tiếp theo ngân sách, món cay/ít béo, hay chỉ món đang còn hàng không?"
        )


    if "popular" in intents:
        top = context["top_products"]
        if not top:
            return "Hiện tại mình chưa có đủ dữ liệu món bán chạy. Bạn có thể xem danh sách món mới nhất ở trang chủ."
        joined = ", ".join(f"{x['name']} ({x['sold_qty']} lượt)" for x in top)
        return _pick_variant(
            f"{query}-{repeated_count}",
            [
                f"Top món bán chạy hiện tại: {joined}.",
                f"Những món đang được gọi nhiều: {joined}.",
                f"Nếu bạn muốn chọn an toàn, mình đề xuất các món này: {joined}.",
            ],
        )

    if "payment" in intents:
        return _pick_variant(
            f"{query}-payment-{repeated_count}",
            [
                (
                    "Bạn có thể chọn VNPay ở bước checkout. Sau khi thanh toán thành công, "
                    "hệ thống sẽ tự cập nhật trạng thái đơn hàng."
                ),
                "Ở trang thanh toán, bạn chọn phương thức VNPay rồi xác nhận giao dịch. Thanh toán xong là đơn sẽ được cập nhật tự động.",
                "Mình gợi ý thanh toán qua VNPay tại checkout để xử lý nhanh. Khi giao dịch thành công, trạng thái đơn sẽ chuyển ngay trong hệ thống.",
            ],
        )

    if "delivery" in intents:
        return _pick_variant(
            f"{query}-delivery-{repeated_count}",
            [
                "Bên mình có hỗ trợ giao hàng theo địa chỉ khi đặt đơn. Bạn cho mình khu vực nhận để kiểm tra phương án giao phù hợp nhé.",
                "Bạn có thể đặt online và chọn giao hàng. Mình cần quận/khu vực của bạn để tư vấn thời gian nhận dự kiến chính xác hơn.",
                "InvenStory có giao hàng, thời gian phụ thuộc khu vực và tình trạng đơn. Bạn gửi giúp mình địa chỉ gần đúng để mình gợi ý nhanh.",
            ],
        )

    if "promotion" in intents:
        discounted = _get_discounted_products(products, only_available=True, limit=6)
        if discounted:
            preview = "\n".join(
                f"- {item['name']}: {item['price_original']} -> {item['price_sale']} (-{int(float(item['discount_percent']))}%)"
                for item in discounted[:4]
            )
            return (
                "Món đang có giảm giá (còn hàng) hiện tại:\n"
                f"{preview}\n"
                "Bạn muốn mình lọc tiếp theo ngân sách hoặc chỉ lấy món giảm giá mạnh nhất không?"
            )
        return _pick_variant(
            f"{query}-promotion-{repeated_count}",
            [
                "Hiện mình chưa thấy món nào đang giảm giá trong dữ liệu còn hàng. Bạn muốn mình gợi ý combo theo ngân sách để tiết kiệm hơn không?",
                "Ưu đãi có thể thay đổi theo thời điểm. Tạm thời chưa có món giảm giá rõ ràng trong dữ liệu hiện tại.",
            ],
        )

    if "order" in intents:
        return _pick_variant(
            f"{query}-order-{repeated_count}",
            [
                "Bạn có thể đặt hàng trực tiếp ở trang sản phẩm: chọn món -> thêm vào giỏ -> checkout -> thanh toán (có VNPay).",
                "Để đặt món nhanh: vào chi tiết sản phẩm, bấm 'Đặt hàng', kiểm tra giỏ rồi xác nhận ở checkout.",
                "Mình có thể hỗ trợ bạn chọn món trước, sau đó bạn chốt đơn tại giỏ hàng và thanh toán VNPay nếu cần.",
            ],
        )

    if "availability" in intents:
        available = [p for p in products if p["status"] == "con hang"][:5]
        if not available:
            return "Hiện tại chưa có món nào trong danh sách còn hàng."
        text = ", ".join(f"{p['name']} ({p['price']})" for p in available)
        return _pick_variant(
            f"{query}-{repeated_count}",
            [
                f"Một số món đang còn hàng: {text}.",
                f"Bạn có thể cân nhắc các món còn hàng sau: {text}.",
                f"Danh sách món sẵn để đặt ngay: {text}.",
            ],
        )

    if "diet" in intents:
        lighter = [p for p in products if any(k in _normalize_text(p["description"]) for k in ["salad", "rau", "nuong", "it beo"])]
        if lighter:
            picks = ", ".join(f"{p['name']} ({p['price']})" for p in lighter[:4])
            return f"Nếu bạn muốn ăn nhẹ/ít béo, bạn có thể thử: {picks}. Bạn thích vị thanh hay cay nhẹ để mình lọc kỹ hơn?"
        return "Mình chưa có tag dinh dưỡng chi tiết cho tất cả món. Bạn cho mình khẩu vị (ít béo, ít ngọt, ít cay) để mình gợi ý gần đúng nhé."

    return (
        "Mình có thể hỗ trợ bạn về sản phẩm, giá, tồn kho, đặt hàng và thanh toán VNPay. "
        "Bạn thử hỏi rõ hơn theo nhu cầu (ví dụ: 'gợi ý combo 3 người dưới 150k') để mình tư vấn nhanh nhé."
    )


def _call_gemini(system_prompt: str, history: List[Dict[str, str]], query: str) -> str:
    """
    Call Gemini model using LangChain wrapper.
    Fallback mechanism with try-except untuk stability.
    """
    try:
        model = LLM(model_name="gemini-2.0-flash")

        # Xây dựng message list từ history
        messages = []
        for item in history[-20:]:
            role = "assistant" if item.get("role") == "assistant" else "user"
            if role == "user":
                messages.append(HumanMessage(content=item.get("content", "")))
            else:
                messages.append(AIMessage(content=item.get("content", "")))

        # Thêm current query
        messages.append(HumanMessage(content=query))

        # Invoke model with system prompt
        response = model.invoke(
            [SystemMessage(content=system_prompt)] + messages
        )

        # Extract text content
        if isinstance(response, AIMessage):
            return _content_to_text(response.content)
        return _content_to_text(response.content if hasattr(response, 'content') else str(response))
    except Exception as e:
        # Log lỗi nhưng không raise - return empty string để dùng fallback
        import traceback
        print(f"Gemini API error: {e}")
        traceback.print_exc()
        return ""


def _content_to_text(content: Any) -> str:
    """Convert various content types to string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text", item)))
            else:
                text_parts.append(str(item))
        return "\n".join(text_parts)
    return str(content)


def _build_style_note(query: str, repeated_count: int) -> str:
    """
    Sinh ghi chú phong cách trả lời cho AI. Có thể mở rộng về sau.
    """
    if repeated_count > 1:
        return "Trả lời thân thiện, linh hoạt, tránh lặp lại, có thể thêm chút hài hước nếu khách hỏi lặp."
    return "Trả lời thân thiện, tự nhiên, ngắn gọn, dễ hiểu, ưu tiên gợi ý món phù hợp."


def chat_once(user_id: str, chat_session_id: str, new_query: str, history: List[Dict[str, str]]) -> str:
    _ = user_id, chat_session_id
    context = get_domain_context()
    context_text = _build_context_text(context, new_query, history)
    intents = _detect_intents(new_query)
    repeated_count = sum(
        1
        for item in history
        if item.get("role") == "user" and _normalize_text(item.get("content", "")) == _normalize_text(new_query)
    )
    style_note = _build_style_note(new_query, repeated_count)

    system_prompt = (
        "Bạn là InvenStory AI, trợ lý tư vấn bán hàng fast food cho website InvenStory.\n\n"
        "## VAI TRO\n"
        "- Tư vấn món phù hợp theo nhu cầu khách (ngân sách, số người, khẩu vị, món còn hàng).\n"
        "- Hỗ trợ câu hỏi về giá, tồn kho, đặt hàng, giao hàng, thanh toán VNPay.\n"
        "- Nếu thiếu thông tin, hỏi lại tối đa 1 câu rõ ràng để chốt nhu cầu.\n\n"
        "## QUY TAC TRA LOI\n"
        "1) Chỉ trả lời nội dung liên quan InvenStory (sản phẩm/dịch vụ bán hàng).\n"
        "2) Không bịa dữ liệu ngoài phần DU LIEU NOI BO.\n"
        "3) Khi gợi ý món, ưu tiên 2-4 lựa chọn có giá và trạng thái còn hàng.\n"
        "4) Nếu món hết hàng, nêu rõ và đề xuất thay thế gần nhất.\n"
        "5) Luôn diễn đạt tiếng Việt tự nhiên, ngắn gọn, linh hoạt, tránh lặp khuôn.\n\n"
        "## PHONG CACH\n"
        f"- {style_note}\n"
        "- Tránh viết dài dòng; ưu tiên thông tin hành động cho bước tiếp theo.\n\n"
        f"## TIN HIEU INTENT PHAT HIEN\n- {', '.join(sorted(intents)) if intents else 'khong ro'}\n\n"
        f"DU LIEU NOI BO:\n{context_text}"
    )

    try:
        answer = _call_gemini(system_prompt, history, new_query)
        if answer:
            return answer
    except Exception:
        pass

    return _fallback_answer(new_query, context, history)


def _is_in_domain(query: str, context: Dict[str, List[Dict[str, str]]]) -> bool:
    """
    Kiểm tra xem câu hỏi có thuộc phạm vi tư vấn sản phẩm, món ăn, dịch vụ không.
    """
    tokens = _tokenize(query)
    for topic in ALLOWED_TOPICS:
        if topic in tokens:
            return True
    for product in context.get("products", []):
        name = _normalize_text(product.get("name", ""))
        if name and name in _normalize_text(query):
            return True
    intents = _detect_intents(query)
    if intents:
        return True
    return False


def _category_bucket(category: str, name: str) -> str:
    """
    Phân loại sản phẩm thành các nhóm chính: main, dessert, drink.
    """
    cat = _normalize_text(category)
    nm = _normalize_text(name)
    if any(k in cat or k in nm for k in ["trang mieng", "dessert", "banh", "pudding", "flan", "lava", "kem"]):
        return "dessert"
    if any(k in cat or k in nm for k in ["nuoc", "drink", "tra", "coffee", "sua", "do uong"]):
        return "drink"
    return "main"


def _pick_variant(key: str, variants: list) -> str:
    """
    Chọn ngẫu nhiên một câu trả lời từ danh sách, giúp chatbot trả lời tự nhiên, nhí nhảnh.
    """
    if not variants:
        return ""
    return random.choice(variants)

def _extract_budget_preferences(query: str) -> dict:
    """
    Phân tích query để xác định người dùng có muốn tráng miệng hoặc đồ uống không.
    """
    normalized = _normalize_text(query)
    return {
        "wants_dessert": any(k in normalized for k in ["trang mieng", "dessert", "banh", "pudding", "flan", "lava", "kem"]),
        "wants_drink": any(k in normalized for k in ["nuoc", "drink", "tra", "coffee", "sua", "do uong"]),
    }

def _build_out_of_scope_reply(query: str) -> str:
    playful_variants = [
        "Ối dồi ôi, câu này hack não quá, AI nhà InvenStory xin phép né nhẹ nha 😝! Mình chỉ giỏi tư vấn món ăn, combo, giá cả, đặt hàng, săn sale thôi á 🍔🥤. Bạn thử hỏi mình món nào ngon, còn hàng, hoặc nhờ gợi ý combo tiết kiệm nhé!",
        "Huhu, câu này ngoài vùng phủ sóng của mình rồi 🥲. Nhưng nếu bạn muốn biết món gì ngon, món nào đang giảm giá, hay cách đặt hàng thì hỏi mình liền nha! 🍕🍟🥤",
        "Câu này mình chịu thua luôn á 😅. Nhưng mà mình cực đỉnh tư vấn đồ ăn, combo tiết kiệm, săn sale, đặt hàng xịn xò nha! Bạn hỏi thử về menu hoặc món bán chạy xem! 🍔✨",
        "Eo ơi, câu này khó quá trời, mình chỉ biết tư vấn món ăn, combo, giá cả, đặt hàng thôi nè! Nếu bạn cần gợi ý món ngon, combo cho nhiều người hay săn ưu đãi thì hỏi mình nha! 😋🍟",
        "Chuyện tình cảm, thời tiết mình chịu nha 😆. Nhưng hỏi về đồ ăn, combo, săn sale thì mình là số 1 luôn! Bạn thử hỏi món nào đang hot hoặc combo tiết kiệm đi! 🍕🔥"
    ]
    import random
    return random.choice(playful_variants)
