import json

from app.services.claude_service import analyze_competitors


with open(
    "data/reliance_products.json",
    "r",
    encoding="utf-8",
) as file:
    reliance = json.load(file)


with open(
    "data/vijay_sales_products.json",
    "r",
    encoding="utf-8",
) as file:
    vijay_sales = json.load(file)


products = reliance + vijay_sales

print("Products sent to Claude:", len(products))
print()
print("Sending data to Claude...")
print()

result = analyze_competitors(products)

print("=" * 70)
print("CLAUDE COMPETITIVE INTELLIGENCE")
print("=" * 70)
print()
print(result)