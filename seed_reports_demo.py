from datetime import datetime
from decimal import Decimal
import random

from src import create_app, db
from src.models import Category, Order, OrderItem, Payment, Product, ProductVariant, User


DEMO_PREFIX = "RPTDEMO4M"


def ensure_customer():
    customer = User.query.filter_by(username="report_demo").first()
    if customer:
        return customer

    customer = User(
        username="report_demo",
        full_name="Khach hang bao cao",
        email="report_demo@invenstory.local",
        role="customer",
        phone="0900000000",
        address="Ho Chi Minh City",
    )
    customer.set_password("123456")
    db.session.add(customer)
    db.session.flush()
    return customer


def ensure_catalog():
    category = Category.query.filter_by(category_code="RPT").first()
    if not category:
        category = Category(category_code="RPT", name="Mon demo bao cao", description="Du lieu demo bieu do")
        db.session.add(category)
        db.session.flush()

    specs = [
        ("RPT-BURGER", "Burger Pho Mai", Decimal("45000")),
        ("RPT-FRIED", "Ga Ran", Decimal("60000")),
        ("RPT-PIZZA", "Pizza Mini", Decimal("85000")),
        ("RPT-TEA", "Tra Dao", Decimal("30000")),
        ("RPT-COMBO", "Combo Gia Dinh", Decimal("145000")),
    ]

    variants = []
    for sku, name, price in specs:
        product = Product.query.filter_by(sku=sku).first()
        if not product:
            product = Product(
                sku=sku,
                category_id=category.id,
                name=name,
                description="San pham demo phuc vu thong ke doanh thu",
                is_available=True,
            )
            db.session.add(product)
            db.session.flush()

        variant = ProductVariant.query.filter_by(product_id=product.id, size_name="M").first()
        if not variant:
            variant = ProductVariant(product_id=product.id, size_name="M", price=price, stock=999)
            db.session.add(variant)
            db.session.flush()

        variants.append((product, variant))

    return variants


def clear_old_demo_data():
    old_orders = Order.query.filter(Order.order_code.like(f"{DEMO_PREFIX}-%")).all()
    for order in old_orders:
        db.session.delete(order)
    db.session.flush()


def create_paid_order(customer, order_code, paid_at, product_variants, month_factor, rng):
    picked_count = rng.randint(1, 3)
    picked = rng.sample(product_variants, picked_count)

    line_items = []
    subtotal = Decimal("0")
    for product, variant in picked:
        qty = rng.randint(1, 4)
        line_total = Decimal(str(variant.price)) * qty
        subtotal += line_total
        line_items.append((product, variant, qty, Decimal(str(variant.price))))

    adjusted = subtotal * Decimal(str(month_factor))
    total_price = max(Decimal("50000"), adjusted.quantize(Decimal("1")))

    order = Order(
        order_code=order_code,
        user_id=customer.id,
        total_price=total_price,
        status="completed",
        shipping_address=customer.address or "Ho Chi Minh City",
        note="Du lieu demo thong ke doanh thu",
        created_at=paid_at,
    )
    db.session.add(order)
    db.session.flush()

    for product, variant, qty, unit_price in line_items:
        db.session.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                variant_id=variant.id,
                quantity=qty,
                price_at_purchase=unit_price,
            )
        )

    db.session.add(
        Payment(
            order_id=order.id,
            payment_method="vnpay",
            amount=total_price,
            payment_status="completed",
            vnp_txn_ref=f"{order.id}{paid_at.strftime('%H%M%S')}",
            vnp_transaction_no=f"DEMO{order.id}",
            vnp_response_code="00",
            created_at=paid_at,
        )
    )

    return float(total_price)


def seed_first_four_months(customer, product_variants, year, intensity, rng):
    monthly_revenue = {m: 0.0 for m in range(1, 5)}

    for month in range(1, 5):
        orders_count = rng.randint(12, 18)
        for index in range(orders_count):
            day = rng.randint(1, 28)
            hour = rng.randint(8, 21)
            minute = rng.randint(0, 59)
            paid_at = datetime(year, month, day, hour, minute)
            code = f"{DEMO_PREFIX}-{year}{month:02d}-{index + 1:02d}-{rng.randint(100, 999)}"
            revenue = create_paid_order(
                customer=customer,
                order_code=code,
                paid_at=paid_at,
                product_variants=product_variants,
                month_factor=intensity.get(month, 1.0),
                rng=rng,
            )
            monthly_revenue[month] += revenue

    return monthly_revenue


def main():
    app = create_app()
    rng = random.Random(2026)

    with app.app_context():
        customer = ensure_customer()
        product_variants = ensure_catalog()
        clear_old_demo_data()

        now_year = datetime.now().year
        first_four_month_shape = {
            1: 0.9,
            2: 1.3,
            3: 1.8,
            4: 2.4,
        }

        current_year_data = seed_first_four_months(customer, product_variants, now_year, first_four_month_shape, rng)

        db.session.commit()

        print(f"Da tao du lieu demo thanh toan VNPay cho thang 1 den thang 4 nam {now_year}.")
        print("Du lieu luu trong bang orders va payments (payment_method='vnpay', payment_status='completed').")
        print("Tong doanh thu demo theo thang:")
        for m in range(1, 5):
            print(f"- Thang {m:02d}: {current_year_data[m]:,.0f} VND")


if __name__ == "__main__":
    main()


