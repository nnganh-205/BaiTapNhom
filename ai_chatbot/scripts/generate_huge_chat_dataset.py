import argparse
import csv
import json
import random
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Dict, List

INTENTS = [
    "greeting",
    "menu",
    "promotion",
    "availability",
    "budget",
    "popular",
    "payment",
    "delivery",
    "order",
    "diet",
]

BUDGET_VALUES = [
    "80k",
    "100k",
    "120k",
    "150k",
    "180k",
    "200k",
    "250k",
    "300k",
    "350k",
    "500k",
]

PEOPLE_VALUES = ["1", "2", "3", "4", "5", "6", "8", "10"]

FOOD_GROUPS = [
    "burger",
    "gà rán",
    "pasta",
    "tráng miệng",
    "đồ uống",
    "pizza",
]

PRODUCT_HINTS = [
    "burger tôm",
    "burger bò phô mai",
    "cánh gà buffalo",
    "gà rán giòn",
    "pasta carbonara",
    "pudding flan",
    "lava cake",
    "nước ngọt có gas",
]

TEMPLATES: Dict[str, List[str]] = {
    "greeting": [
        "xin chào",
        "hello shop",
        "alo",
        "ad ơi",
        "shop ơi",
        "ê",
    ],
    "menu": [
        "menu có gì vậy",
        "thực đơn hôm nay",
        "có món {food_group} không",
        "gợi ý món đi",
        "cho xem menu nhanh",
        "tráng miệng là gì",
        "đồ uống có gì",
    ],
    "promotion": [
        "món nào đang giảm giá",
        "có khuyến mãi gì không",
        "đang sale món nào",
        "ưu đãi hôm nay",
        "cho mình list món đang giảm",
        "deal ngon hiện tại",
    ],
    "availability": [
        "{product_hint} còn hàng không",
        "check tồn kho giúp mình",
        "món nào đang còn",
        "còn món nào order liền được",
        "{food_group} còn không",
    ],
    "budget": [
        "{budget} ăn được gì",
        "gợi ý combo {people} người dưới {budget}",
        "mình có {budget} thôi",
        "tư vấn món tầm {budget}",
        "{people} người ngân sách {budget} nhé",
    ],
    "popular": [
        "món bán chạy là gì",
        "top món đi",
        "nhiều người đặt món nào",
        "món hot bên mình",
    ],
    "payment": [
        "thanh toán vnpay sao",
        "hướng dẫn thanh toán",
        "cod hay vnpay",
        "trả tiền kiểu gì",
    ],
    "delivery": [
        "ship bao lâu",
        "có giao hàng không",
        "phí ship bao nhiêu",
        "khu vực này giao được không",
    ],
    "order": [
        "đặt hàng như nào",
        "mua món này giúp mình",
        "cách order",
        "chốt đơn sao vậy",
    ],
    "diet": [
        "món ít béo có không",
        "mình ăn cay nhẹ thôi",
        "gợi ý món dễ ăn",
        "đang ăn kiêng nên chọn gì",
    ],
}

COLLOQUIAL_REPLACEMENTS = {
    "không": "ko",
    "được": "dc",
    "gì": "j",
    "mình": "mk",
    "bao nhiêu": "bn",
    "như nào": "sao",
    "thế nào": "sao",
    "vậy": "v",
    "đi": "điii",
}

FRAGMENT_POOL = [
    "menu?",
    "đang giảm?",
    "ship?",
    "vnpay?",
    "còn hàng k",
    "tráng miệng?",
    "burger còn ko",
    "giá bn",
    "combo 2 người",
    "ít béo",
    "top món",
]


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _fill_slots(template: str, rng: random.Random) -> str:
    return template.format(
        budget=rng.choice(BUDGET_VALUES),
        people=rng.choice(PEOPLE_VALUES),
        food_group=rng.choice(FOOD_GROUPS),
        product_hint=rng.choice(PRODUCT_HINTS),
    )


def _apply_colloquial(text: str, rng: random.Random) -> str:
    result = text
    for src, dst in COLLOQUIAL_REPLACEMENTS.items():
        if src in result and rng.random() < 0.35:
            result = result.replace(src, dst)

    # Drop polite suffixes occasionally to simulate short normal texting.
    for suffix in [" nhé", " nha", " ạ", " giúp mình", " đi"]:
        if suffix in result and rng.random() < 0.3:
            result = result.replace(suffix, "")

    if rng.random() < 0.18:
        result = _strip_accents(result)

    if rng.random() < 0.22:
        result = result.replace("?", "")

    return " ".join(result.split())


def _build_text(intents: List[str], rng: random.Random) -> str:
    # Small chance to create super-short fragments like real messages.
    if rng.random() < 0.12:
        return rng.choice(FRAGMENT_POOL)

    parts = []
    for intent in intents:
        template = rng.choice(TEMPLATES[intent])
        parts.append(_fill_slots(template, rng))

    if len(parts) > 1:
        joiner = rng.choice(["; ", " / ", ", ", " | "])
        text = joiner.join(parts)
    else:
        text = parts[0]

    return _apply_colloquial(text, rng)


def _choose_intents(rng: random.Random) -> List[str]:
    primary = rng.choices(
        population=INTENTS,
        weights=[8, 15, 14, 11, 14, 9, 8, 7, 8, 6],
        k=1,
    )[0]

    intents = [primary]
    if rng.random() < 0.24:
        secondary_candidates = [it for it in INTENTS if it != primary]
        secondary = rng.choice(secondary_candidates)
        intents.append(secondary)

    return sorted(set(intents))


def _split_rows(rows: List[dict], train_ratio: float, dev_ratio: float) -> Dict[str, List[dict]]:
    total = len(rows)
    train_end = int(total * train_ratio)
    dev_end = train_end + int(total * dev_ratio)
    return {
        "train": rows[:train_end],
        "dev": rows[train_end:dev_end],
        "test": rows[dev_end:],
    }


def _write_jsonl(path: Path, rows: List[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_csv(path: Path, rows: List[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "text", "intents", "primary_intent", "is_fragment", "source"],
        )
        writer.writeheader()
        for row in rows:
            csv_row = dict(row)
            csv_row["intents"] = "|".join(row["intents"])
            writer.writerow(csv_row)


def generate_dataset(total_samples: int, seed: int) -> List[dict]:
    rng = random.Random(seed)
    rows = []

    for idx in range(1, total_samples + 1):
        intents = _choose_intents(rng)
        text = _build_text(intents, rng)
        rows.append(
            {
                "id": f"syn_{idx:08d}",
                "text": text,
                "intents": intents,
                "primary_intent": intents[0],
                "is_fragment": len(text.split()) <= 3,
                "source": "synthetic_v1",
            }
        )

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a huge synthetic Vietnamese chatbot dataset.")
    parser.add_argument("--total-samples", type=int, default=200000, help="Total rows to generate.")
    parser.add_argument("--seed", type=int, default=20260414, help="Random seed for reproducibility.")
    parser.add_argument("--train-ratio", type=float, default=0.9)
    parser.add_argument("--dev-ratio", type=float, default=0.05)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("ai_chatbot/data/synthetic"),
        help="Output directory for generated files.",
    )
    args = parser.parse_args()

    if args.total_samples < 1000:
        raise ValueError("--total-samples should be at least 1000 for meaningful coverage.")

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = generate_dataset(total_samples=args.total_samples, seed=args.seed)
    splits = _split_rows(rows, train_ratio=args.train_ratio, dev_ratio=args.dev_ratio)

    for split_name, split_rows in splits.items():
        _write_jsonl(out_dir / f"{split_name}.jsonl", split_rows)
        _write_csv(out_dir / f"{split_name}.csv", split_rows)

    intent_counter = Counter()
    fragment_counter = 0
    for row in rows:
        for intent in row["intents"]:
            intent_counter[intent] += 1
        fragment_counter += int(bool(row["is_fragment"]))

    stats = {
        "total_samples": len(rows),
        "seed": args.seed,
        "splits": {name: len(split_rows) for name, split_rows in splits.items()},
        "intent_frequency": dict(intent_counter),
        "fragment_count": fragment_counter,
        "fragment_ratio": round(fragment_counter / max(1, len(rows)), 4),
    }

    with (out_dir / "stats.json").open("w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

