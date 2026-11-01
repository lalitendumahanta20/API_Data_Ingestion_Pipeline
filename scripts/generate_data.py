
import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

OUTPUT_DIR = Path("sample_data")


def generate_data(count=1000, seed=42):
    random.seed(seed)
    OUTPUT_DIR.mkdir(exist_ok=True)

    customers = []
    orders = []

    now = datetime.now(timezone.utc)

    for customer_id in range(1, count + 1):
        customers.append({
            "customer_id": customer_id,
            "customer_name": f"Customer_{customer_id}",
            "email": f"customer{customer_id}@example.com",
            "created_at": (
                now - timedelta(days=random.randint(1, 365))
            ).isoformat(),
            "updated_at": now.isoformat()
        })

        # Generate approximately two orders per customer
        for order_number in range(2):
            order_id = (customer_id * 10) + order_number

            orders.append({
                "order_id": order_id,
                "customer_id": customer_id,
                "order_amount": round(random.uniform(10, 1000), 2),
                "order_status": random.choice(
                    ["PENDING", "COMPLETED", "CANCELLED"]
                ),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            })

    with open(OUTPUT_DIR / "customers.json", "w") as file:
        json.dump(customers, file, indent=2)

    with open(OUTPUT_DIR / "orders.json", "w") as file:
        json.dump(orders, file, indent=2)

    print(f"Generated {len(customers)} customers")
    print(f"Generated {len(orders)} orders")
    print(f"Random seed: {seed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    generate_data(args.count, args.seed)
