
import csv
from decimal import Decimal
from pathlib import Path

# Location of our demonstration product database
PRODUCT_FILE = Path(__file__).parent / "products.csv"


def calculate_basket(items: list[dict], budget: float) -> dict:
    """
    Calculate a shopping basket using product IDs and quantities.

    items: list of dictionaries containing id and quantity.
    budget: maximum amount the customer wants to spend.
    """

    print("\n[AGENT TOOL CALLED] calculate_basket")

    if budget < 0:
        return {"error": "Budget cannot be negative."}

    # Read the product database
    with open(PRODUCT_FILE, "r", encoding="utf-8-sig", newline="") as file:
        products = {
            int(row["id"]): row
            for row in csv.DictReader(file)
        }

    basket = []
    total = Decimal("0.00")
    problems = []

    for item in items:
        product_id = int(item["id"])
        quantity = int(item["quantity"])

        if quantity <= 0:
            problems.append("Quantity must be greater than zero.")
            continue

        if product_id not in products:
            problems.append(f"Product ID {product_id} not found.")
            continue

        product = products[product_id]
        available_stock = int(product["stock"])

        if quantity > available_stock:
            problems.append(
                f"{product['name']}: only {available_stock} available."
            )
            continue

        price = Decimal(product["price"])
        subtotal = price * quantity
        total += subtotal

        basket.append({
            "id": product_id,
            "name": product["name"],
            "quantity": quantity,
            "unit_price": float(price),
            "subtotal": float(subtotal)
        })

    budget_amount = Decimal(str(budget))
    within_budget = total <= budget_amount

    return {
        "basket": basket,
        "total": float(total),
        "budget": float(budget_amount),
        "remaining_budget": float(budget_amount - total),
        "within_budget": within_budget,
        "problems": problems,
        "ready_for_approval": within_budget and not problems and bool(basket),
        "note": "Simulated basket only. No order has been placed."
    }


# Test the tool directly before connecting Gemini
if __name__ == "__main__":

    test_items = [
        {"id": 2, "quantity": 2},
        {"id": 3, "quantity": 1},
        {"id": 5, "quantity": 1}
    ]

    result = calculate_basket(
        items=test_items,
        budget=50.00
    )

    print("\nCOSTCO SHOPPING BASKET")
    print("---------------------")

    for product in result["basket"]:
        print(
            product["name"],
            "| Quantity:", product["quantity"],
            "| Subtotal: $", product["subtotal"]
        )

    print("\nTotal: $", result["total"])
    print("Budget: $", result["budget"])
    print("Remaining: $", result["remaining_budget"])
    print("Within budget:", result["within_budget"])
    print("Ready for approval:", result["ready_for_approval"])
    print("Problems:", result["problems"])
