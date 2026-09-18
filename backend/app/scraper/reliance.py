from datetime import datetime
from pathlib import Path
import json
import re

from playwright.sync_api import sync_playwright


OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "reliance_products.json"
)


def clean_text(text):
    return " ".join(text.split()).strip()


def clean_product_name(text, category):
    """
    Extract the actual product name from the product-card
    text captured from Reliance Digital.

    The scraper sometimes captures UI text such as:
    Bank Offer, Compare, delivery information, etc.
    """

    text = clean_text(text)

    # -------------------------------------------------
    # Remove common Reliance Digital UI text
    # -------------------------------------------------

    ui_patterns = [
        r"No Cost EMI",
        r"Bank Offer",
        r"Compare",
        r"Extra Deals Available",
        r"Free delivery by .*?(?=$|Out Of Stock|Notify Me)",
        r"Out Of Stock",
        r"Notify Me",
        r"Price Drop ends in \d+\s*:\s*\d+\s*:\s*\d+",
    ]

    for pattern in ui_patterns:
        text = re.sub(
            pattern,
            " ",
            text,
            flags=re.IGNORECASE,
        )

    # -------------------------------------------------
    # Remove price / MRP / discount information
    # -------------------------------------------------

    text = re.sub(
        r"MRP\s*₹?\s*[\d,]+(?:\.\d+)?",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"₹\s*[\d,]+(?:\.\d+)?",
        " ",
        text,
    )

    text = re.sub(
        r"\d+%\s*OFF",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # -------------------------------------------------
    # Remove ratings
    # -------------------------------------------------

    text = re.sub(
        r"[★☆]\s*[0-5](?:\.\d+)?",
        " ",
        text,
    )

    text = re.sub(
        r"\b[0-5](?:\.\d+)?\s*(?:stars?)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # -------------------------------------------------
    # Remove review counts
    # -------------------------------------------------

    text = re.sub(
        r"\(\s*\d+\s*\)",
        " ",
        text,
    )

    # -------------------------------------------------
    # Product cards often use "|" to separate the
    # actual title from specifications.
    #
    # For mobiles and some other categories, the first
    # section is normally the cleanest product title.
    # -------------------------------------------------

    if "|" in text:
        parts = [
            clean_text(part)
            for part in text.split("|")
            if clean_text(part)
        ]

        if parts:
            text = parts[0]

    # -------------------------------------------------
    # Remove delivery/UI text that may remain at the
    # beginning or end.
    # -------------------------------------------------

    text = re.sub(
        r"Free delivery.*$",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"Extra Deals Available.*$",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"Out Of Stock.*$",
        " ",
        text,
        flags=re.IGNORECASE,
    )

    # -------------------------------------------------
    # Final cleanup
    # -------------------------------------------------

    text = clean_text(text)

    # Remove dangling separators
    text = re.sub(
        r"^[|,\-:]+",
        "",
        text,
    )

    text = re.sub(
        r"[|,\-:]+$",
        "",
        text,
    )

    return clean_text(text)


def extract_brand(product_name):
    """
    Extract the brand from the beginning of the
    cleaned product name.
    """

    if not product_name:
        return None

    known_brands = [
        "Apple",
        "Samsung",
        "vivo",
        "Vivo",
        "realme",
        "Realme",
        "OnePlus",
        "Oppo",
        "OPPO",
        "Xiaomi",
        "Redmi",
        "Motorola",
        "Nothing",
        "Google",
        "Asus",
        "ASUS",
        "Lenovo",
        "HP",
        "Dell",
        "Acer",
        "MSI",
        "LG",
        "Sony",
        "TCL",
        "Hisense",
        "Haier",
        "Voltas",
        "Daikin",
        "Blue Star",
        "Carrier",
        "Whirlpool",
        "Bosch",
        "IFB",
        "Godrej",
        "Panasonic",
        "Lloyd",
        "O General",
        "Hitachi",
        "BPL",
        "LYF",
        "Sharp",
        "Karbonn",
    ]

    lower_name = product_name.lower()

    for brand in known_brands:
        if lower_name.startswith(
            brand.lower() + " "
        ):
            return brand

        if lower_name == brand.lower():
            return brand

    return product_name.split()[0]


def extract_product_data(
    text,
    url,
    category,
):
    text = clean_text(text)

    # -------------------------------------------------
    # Price
    # -------------------------------------------------

    price = None

    price_match = re.search(
        r"₹\s*([\d,]+(?:\.\d+)?)",
        text,
    )

    if price_match:
        price = float(
            price_match.group(1).replace(",", "")
        )

    # -------------------------------------------------
    # MRP
    # -------------------------------------------------

    mrp = None

    mrp_match = re.search(
        r"MRP\s*₹\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if mrp_match:
        mrp = float(
            mrp_match.group(1).replace(",", "")
        )

    # -------------------------------------------------
    # Discount
    # -------------------------------------------------

    discount = None

    discount_match = re.search(
        r"(\d+)%\s*OFF",
        text,
        re.IGNORECASE,
    )

    if discount_match:
        discount = int(
            discount_match.group(1)
        )

    # -------------------------------------------------
    # Rating
    # -------------------------------------------------

    rating = None

    rating_match = re.search(
        r"([0-5](?:\.\d+)?)\s*(?:★|stars?)",
        text,
        re.IGNORECASE,
    )

    if rating_match:
        rating = float(
            rating_match.group(1)
        )

    # -------------------------------------------------
    # Review count
    # -------------------------------------------------

    review_count = None

    review_match = re.search(
        r"\((\d+)\)",
        text,
    )

    if review_match:
        review_count = int(
            review_match.group(1)
        )

    # -------------------------------------------------
    # Product name
    # -------------------------------------------------

    product_name = clean_product_name(
        text,
        category,
    )

    # -------------------------------------------------
    # Brand
    # -------------------------------------------------

    brand = extract_brand(
        product_name
    )

    return {
        "retailer": "Reliance Digital",
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "price": price,
        "mrp": mrp,
        "discount": discount,
        "rating": rating,
        "review_count": review_count,
        "availability": None,
        "product_url": url,
        "scraped_at": datetime.now().isoformat(),
    }


def scrape_reliance(
    category,
    category_url,
    limit=30,
):
    products = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 900,
            },
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )

        print()
        print(
            f"Opening {category}:"
        )

        print(category_url)

        page.goto(
            category_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print(
            f"Page title: {page.title()}"
        )

        # -------------------------------------------------
        # Scroll
        # -------------------------------------------------

        for _ in range(8):

            page.mouse.wheel(
                0,
                1800,
            )

            page.wait_for_timeout(
                1500
            )

        # -------------------------------------------------
        # Collect links
        # -------------------------------------------------

        links = page.locator(
            "a"
        ).evaluate_all(
            """
            elements => elements.map(a => ({
                text: a.innerText,
                href: a.href
            }))
            """
        )

        # -------------------------------------------------
        # Keep richest text for each product URL
        # -------------------------------------------------

        product_links = {}

        for item in links:

            href = item.get("href")

            text = clean_text(
                item.get("text", "")
            )

            if not href:
                continue

            if (
                "reliancedigital.in"
                not in href
            ):
                continue

            if "/product/" not in href:
                continue

            if text.lower() in [
                "view product",
                "view details",
                "buy now",
                "add to cart",
            ]:
                continue

            if not text:
                continue

            if href not in product_links:

                product_links[href] = text

            else:

                existing_text = (
                    product_links[href]
                )

                if len(text) > len(
                    existing_text
                ):
                    product_links[href] = text

        # -------------------------------------------------
        # Parse products
        # -------------------------------------------------

        for url, text in product_links.items():

            # Product cards should contain a price.
            if not re.search(
                r"₹\s*[\d,]+",
                text,
            ):
                continue

            product = extract_product_data(
                text,
                url,
                category,
            )

            if not product[
                "product_name"
            ]:
                continue

            if product[
                "product_name"
            ].lower() in [
                "view product",
                "view details",
                "buy now",
                "add to cart",
            ]:
                continue

            products.append(
                product
            )

            if len(products) >= limit:
                break

        browser.close()

    # -------------------------------------------------
    # Save JSON
    # -------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Load existing products
    existing_products = []

    if OUTPUT_FILE.exists():

        try:

            with open(
                OUTPUT_FILE,
                "r",
                encoding="utf-8",
            ) as f:

                existing_products = json.load(
                    f
                )

                if not isinstance(
                    existing_products,
                    list,
                ):
                    existing_products = []

        except (
            json.JSONDecodeError,
            FileNotFoundError,
        ):

            existing_products = []

    # -------------------------------------------------
    # Remove old products from the same
    # retailer/category
    # -------------------------------------------------

    existing_products = [
        product
        for product in existing_products
        if not (
            product.get(
                "retailer"
            )
            == "Reliance Digital"
            and product.get(
                "category"
            )
            == category
        )
    ]

    # Add newly scraped products
    all_products = (
        existing_products
        + products
    )

    # -------------------------------------------------
    # Save combined dataset
    # -------------------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            all_products,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print("=" * 50)

    print(
        f"Category: {category}"
    )

    print(
        f"Products collected: "
        f"{len(products)}"
    )

    print(
        f"Total products in dataset: "
        f"{len(all_products)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print("=" * 50)

    return products


if __name__ == "__main__":

    scrape_reliance(
        "Laptops",
        "https://www.reliancedigital.in/collection/laptops",
        limit=30,
    )