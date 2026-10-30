
import csv
from pathlib import Path

# Find our Costco product database
PRODUCT_FILE = Path(__file__).parent / "products.csv"



def search_products(keyword: str, vegetarian_only: bool):

    """
    Search the Costco demonstration product database.
    """

    print(
        f"\n[AGENT TOOL CALLED] search_products "
        f"| keyword={keyword} "
        f"| vegetarian_only={vegetarian_only}"
    )


    results = []

    with open(PRODUCT_FILE, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for product in reader:

            # Check whether the product matches the search
            matches_keyword = (
                keyword.lower() in product["name"].lower()
                or keyword.lower() in product["category"].lower()
            )

            # Check dietary preference
            matches_diet = (
                not vegetarian_only
                or product["vegetarian"].lower() == "yes"
            )

            if matches_keyword and matches_diet:
                results.append({
                    "id": int(product["id"]),
                    "name": product["name"],
                    "category": product["category"],
                    "price": float(product["price"]),
                    "stock": int(product["stock"]),
                    "vegetarian": product["vegetarian"]
                })

    return results


# Test our shopping tool
if __name__ == "__main__":

    print("COSTCO PRODUCT SEARCH")
    print("--------------------")

    products = search_products(
        keyword="Vegetables",
        vegetarian_only=True
    )

    for product in products:
        print(
            product["name"],
            "| Price: $", product["price"],
            "| Stock:", product["stock"]
        )
