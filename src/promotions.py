import json
import os
from datetime import datetime
from typing import Dict, List

DEFAULT_PROMOTIONS: List[Dict] = [
    {
        "code": "FREESHIP90",
        "name": "Đơn từ 90.000đ miễn phí ship",
        "type": "free_ship",
        "enabled": True,
        "min_subtotal": 90000,
    },
    {
        "code": "SAVE30_130",
        "name": "Đơn từ 130.000đ giảm 30.000đ",
        "type": "fixed_discount",
        "enabled": True,
        "min_subtotal": 130000,
        "discount_amount": 30000,
    },
    {
        "code": "GROUP60_300",
        "name": "Combo nhóm từ 300.000đ giảm 60.000đ",
        "type": "group_combo",
        "enabled": True,
        "min_subtotal": 300000,
        "min_items": 3,
        "discount_amount": 60000,
    },
    {
        "code": "LUCKY15",
        "name": "Khung giờ vàng giảm 15%",
        "type": "lucky_hour",
        "enabled": True,
        "min_subtotal": 150000,
        "discount_percent": 15,
        "min_stock": 60,
        "time_windows": [[6, 12], [13, 15]],
    },
]


def _promotions_path() -> str:
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir, "..", "instance", "promotions.json")


def load_promotions() -> List[Dict]:
    path = _promotions_path()
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        save_promotions(DEFAULT_PROMOTIONS)
        return [dict(item) for item in DEFAULT_PROMOTIONS]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        save_promotions(DEFAULT_PROMOTIONS)
        return [dict(item) for item in DEFAULT_PROMOTIONS]

    if not isinstance(data, list):
        save_promotions(DEFAULT_PROMOTIONS)
        return [dict(item) for item in DEFAULT_PROMOTIONS]

    has_changes = False
    for item in data:
        code = str(item.get("code", "")).upper()
        promo_type = str(item.get("type", "")).strip()

        if promo_type in {"fixed_discount", "group_combo"}:
            if "discount_mode" not in item:
                # Legacy records used fixed amount by default.
                item["discount_mode"] = "amount"
                has_changes = True
            if "discount_amount" not in item:
                item["discount_amount"] = 0
                has_changes = True
            if "discount_percent" not in item:
                item["discount_percent"] = 0
                has_changes = True

        if code == "LUCKY15":
            if "tồn kho" in str(item.get("name", "")):
                item["name"] = "Khung giờ vàng giảm 15%"
                has_changes = True
            if "time_windows" not in item:
                item["time_windows"] = [[6, 12], [13, 15]]
                has_changes = True
            elif item.get("time_windows") == [[9, 12], [13, 15]]:
                item["time_windows"] = [[6, 12], [13, 15]]
                has_changes = True
            else:
                cleaned_windows: List[List[int]] = []
                for window in item.get("time_windows", []):
                    if not isinstance(window, list) or len(window) != 2:
                        continue
                    try:
                        start_h = int(window[0])
                        end_h = int(window[1])
                    except (TypeError, ValueError):
                        continue
                    if 0 <= start_h <= 23 and 1 <= end_h <= 24 and start_h < end_h:
                        cleaned_windows.append([start_h, end_h])
                if not cleaned_windows:
                    cleaned_windows = [[6, 12], [13, 15]]
                if cleaned_windows != item.get("time_windows"):
                    item["time_windows"] = cleaned_windows
                    has_changes = True

    if has_changes:
        save_promotions(data)

    return data


def save_promotions(promotions: List[Dict]) -> None:
    path = _promotions_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(promotions, f, ensure_ascii=False, indent=2)


def _promo_map(promotions: List[Dict]) -> Dict[str, Dict]:
    return {str(item.get("code", "")).upper(): item for item in promotions}


def _is_in_any_window(now: datetime, windows: List[List[int]]) -> bool:
    current_hour = now.hour
    for window in windows or []:
        if len(window) != 2:
            continue
        start, end = int(window[0]), int(window[1])
        if start <= current_hour < end:
            return True
    return False


def _format_time_windows(windows: List[List[int]]) -> str:
    parts: List[str] = []
    for window in windows or []:
        if len(window) != 2:
            continue
        start, end = int(window[0]), int(window[1])
        parts.append(f"{start:02d}:00-{end:02d}:00")
    return " hoặc ".join(parts)


def evaluate_checkout_pricing(
    cart_items: List[Dict],
    subtotal: float,
    promo_code: str = "",
    now: datetime | None = None,
) -> Dict:
    shipping_fee = 15000.0
    shipping_discount = 0.0
    promotion_discount = 0.0
    applied_promotions: List[str] = []
    messages: List[str] = []

    promotions = load_promotions()
    promo_by_code = _promo_map(promotions)
    check_time = now or datetime.now()

    def _evaluate_single(promo: Dict) -> Dict:
        promo_type = promo.get("type")
        code = str(promo.get("code", "")).upper()
        min_subtotal = float(promo.get("min_subtotal", 0))

        if subtotal < min_subtotal:
            return {
                "eligible": False,
                "message": f"Mã {code} yêu cầu đơn tối thiểu {min_subtotal:,.0f}đ.",
                "shipping_discount": 0.0,
                "promotion_discount": 0.0,
            }

        if promo_type == "free_ship":
            return {
                "eligible": True,
                "message": "",
                "shipping_discount": shipping_fee,
                "promotion_discount": 0.0,
            }

        if promo_type == "fixed_discount":
            amount = float(promo.get("discount_amount", 0))
            percent = max(0.0, min(1.0, float(promo.get("discount_percent", 0)) / 100.0))
            mode = str(promo.get("discount_mode", "")).strip().lower()
            if mode == "percent":
                best_discount = subtotal * percent
            elif mode == "amount":
                best_discount = amount
            else:
                # Backward-compatible fallback for old records without discount_mode.
                percent_discount = subtotal * percent if percent > 0 else 0.0
                best_discount = percent_discount if percent_discount > 0 else amount
            return {
                "eligible": True,
                "message": "",
                "shipping_discount": 0.0,
                "promotion_discount": min(best_discount, subtotal),
            }

        if promo_type == "group_combo":
            amount = float(promo.get("discount_amount", 0))
            percent = max(0.0, min(1.0, float(promo.get("discount_percent", 0)) / 100.0))
            mode = str(promo.get("discount_mode", "")).strip().lower()
            min_items = int(promo.get("min_items", 1))
            total_qty = sum(int(item.get("quantity", 0)) for item in cart_items)
            if total_qty < min_items:
                return {
                    "eligible": False,
                    "message": f"Mã {code} cần tối thiểu {min_items} món trong đơn.",
                    "shipping_discount": 0.0,
                    "promotion_discount": 0.0,
                }
            return {
                "eligible": True,
                "message": "",
                "shipping_discount": 0.0,
                "promotion_discount": min(
                    (subtotal * percent if mode == "percent" else amount) if mode in {"percent", "amount"}
                    else (subtotal * percent if percent > 0 else amount),
                    subtotal,
                ),
            }

        if promo_type == "lucky_hour":
            windows = promo.get("time_windows", [[6, 12], [13, 15]])
            if not _is_in_any_window(check_time, windows):
                display_windows = _format_time_windows(windows) or "khung giờ quy định"
                return {
                    "eligible": False,
                    "message": f"Mã LUCKY15 chỉ áp dụng trong khung giờ {display_windows}.",
                    "shipping_discount": 0.0,
                    "promotion_discount": 0.0,
                }
            percent = float(promo.get("discount_percent", 0)) / 100.0
            eligible_total = sum(
                float(item.get("line_total", 0))
                for item in cart_items
                if bool(item.get("is_lucky_item"))
            )
            if eligible_total <= 0:
                return {
                    "eligible": False,
                    "message": "Giỏ hàng hiện chưa có món trong khung giờ vàng để áp dụng LUCKY15.",
                    "shipping_discount": 0.0,
                    "promotion_discount": 0.0,
                }

            # Golden-hour orders that pass min_subtotal also get free shipping.
            lucky_free_ship_threshold = float(promo.get("free_ship_min_subtotal", min_subtotal))
            lucky_shipping_discount = shipping_fee if subtotal >= lucky_free_ship_threshold else 0.0
            return {
                "eligible": True,
                "message": "",
                "shipping_discount": lucky_shipping_discount,
                "promotion_discount": eligible_total * percent,
            }

        return {
            "eligible": False,
            "message": f"Mã {code} chưa được hỗ trợ.",
            "shipping_discount": 0.0,
            "promotion_discount": 0.0,
        }

    code = (promo_code or "").strip().upper()
    selected = promo_by_code.get(code) if code else None

    if code and not selected:
        messages.append("Mã giảm giá không tồn tại.")
    elif code and not selected.get("enabled"):
        messages.append("Mã giảm giá hiện đã tạm ngưng.")
    elif selected:
        result = _evaluate_single(selected)
        if result["eligible"]:
            shipping_discount = result["shipping_discount"]
            promotion_discount = result["promotion_discount"]
            applied_promotions.append(code)
        else:
            messages.append(result["message"])

    total = subtotal + shipping_fee - shipping_discount - promotion_discount
    total = max(total, 0)

    return {
        "shipping_fee": shipping_fee,
        "shipping_discount": shipping_discount,
        "promotion_discount": promotion_discount,
        "applied_promotions": applied_promotions,
        "messages": messages,
        "grand_total": total,
        "promo_code": code,
    }


def get_checkout_promo_options(cart_items: List[Dict], subtotal: float, now: datetime | None = None) -> List[Dict]:
    promotions = load_promotions()
    check_time = now or datetime.now()
    options: List[Dict] = []

    for promo in promotions:
        code = str(promo.get("code", "")).upper()
        if not code:
            continue

        # Lucky15 is shown only in configured golden-hour windows.
        if promo.get("type") == "lucky_hour":
            windows = promo.get("time_windows", [[6, 12], [13, 15]])
            if not _is_in_any_window(check_time, windows):
                continue

        if not promo.get("enabled"):
            options.append(
                {
                    "code": code,
                    "name": promo.get("name", code),
                    "eligible": False,
                    "reason": "Mã đang tạm ngưng.",
                }
            )
            continue

        result = evaluate_checkout_pricing(cart_items, subtotal, promo_code=code, now=check_time)
        eligible = code in result.get("applied_promotions", []) and not result.get("messages")
        reason = "" if eligible else (result.get("messages") or ["Chưa đủ điều kiện."])[0]
        options.append(
            {
                "code": code,
                "name": promo.get("name", code),
                "eligible": eligible,
                "reason": reason,
            }
        )

    return options


def is_lucky_hour_now(now: datetime | None = None) -> bool:
    check_time = now or datetime.now()
    for promo in load_promotions():
        if str(promo.get("code", "")).upper() != "LUCKY15":
            continue
        if not promo.get("enabled"):
            return False
        return _is_in_any_window(check_time, promo.get("time_windows", [[6, 12], [13, 15]]))
    return False

