import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "vijay_sales_products.json"
)


CATEGORIES = {
    "Laptops": "https://www.vijaysales.com/c/laptops",

    "Televisions": (
        "https://www.vijaysales.com/c/televisions/"
        "category-uid/buy-products-televisions"
        "?categories=Products"
    ),

    "Air Conditioners": (
        "https://www.vijaysales.com/c/air-conditioners"
    ),

    "Washing Machines": (
        "https://www.vijaysales.com/c/washing-machines"
    ),

    "Mobiles": (
        "https://www.vijaysales.com/c/mobiles"
    ),
}


CATEGORY_KEYWORDS = {
    "Laptops": [
        "laptop",
        "notebook",
        "macbook",
        "chromebook",
        "gaming laptop",
        "ultrabook",
    ],

    "Air Conditioners": [
        "air conditioner",
        "airconditioner",
        "split ac",
        "window ac",
        "inverter ac",
        " ac",
        "ac ",
    ],

    "Washing Machines": [
        "washing machine",
        "fully automatic",
        "semi automatic",
        "front load",
        "top load",
        "washer",
    ],

    "Mobiles": [
        "iphone",
        "smartphone",
        "mobile phone",
        "android phone",
        "galaxy s",
        "galaxy a",
        "galaxy m",
        "oneplus",
        "pixel",
        "redmi",
        "realme",
        "vivo",
        "oppo",
        "motorola",
        "nothing phone",
        "poco",
        "iqoo",
    ],
}


def clean_text(text):
    text = re.sub(
        r"\s+",
        " ",
        text or "",
    )

    return text.strip()


def extract_price(text):

    prices = re.findall(
        r"₹\s*([\d,]+(?:\.\d+)?)",
        text or "",
    )

    values = []

    for price in prices:

        try:

            value = float(
                price.replace(",", "")
            )

            if value >= 500:
                values.append(value)

        except ValueError:
            continue

    if not values:
        return None

    return max(values)


def clean_product_name(text):

    text = clean_text(text)

    remove_patterns = [
        r"Buy Now",
        r"Add to Cart",
        r"Add To Cart",
        r"Quick View",
        r"Wishlist",
        r"Compare",
        r"EMI",
        r"Exchange Offer",
        r"Special Price",
        r"Limited Time Offer",
        r"View Details",
    ]

    for pattern in remove_patterns:

        text = re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE,
        )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip(" -|")


def matches_category(product_name, category):

    name = product_name.lower()

    # -----------------------------------------------
    # TELEVISION
    # -----------------------------------------------

    if category == "Televisions":

        # Since this URL is already the Vijay Sales
        # television category, only remove products
        # that are clearly unrelated.
        bad_keywords = [
            "iphone",
            "smartphone",
            "mobile phone",
            "ipad",
            "tablet",
            "macbook",
            "laptop",
            "playstation",
            "ps5",
            "ps4",
            "xbox",
            "controller",
            "headphone",
            "earphone",
            "earbuds",
            "keyboard",
            "mouse",
            "air fryer",
            "refrigerator",
            "washing machine",
            "microwave",
            "camera",
            "smart watch",
            "fitness band",
        ]

        if any(
            keyword in name
            for keyword in bad_keywords
        ):
            return False

        # Accept normal television terminology.
        tv_keywords = [
            "tv",
            "television",
            "smart tv",
            "android tv",
            "google tv",
            "led",
            "oled",
            "qled",
            "qned",
            "mini led",
            "4k",
            "8k",
            "uhd",
            "full hd",
            "bravia",
            "nanocell",
            "crystal",
            "tizen",
            "webos",
            "neo qled",
        ]

        if any(
            keyword in name
            for keyword in tv_keywords
        ):
            return True

        # Common TV screen sizes.
        size_match = re.search(
            r'\b(?:24|32|40|42|43|48|50|55|58|65|70|75|77|83|85|98)\s*(?:inch|in|")',
            name,
        )

        if size_match:
            return True

        # If it has a recognised TV brand and isn't
        # obviously another category, accept it.
        tv_brands = [
            "samsung",
            "lg ",
            "sony",
            "tcl",
            "hisense",
            "vu ",
            "xiaomi",
            "oneplus",
            "acer",
            "toshiba",
            "panasonic",
            "motorola",
        ]

        if any(
            brand in name
            for brand in tv_brands
        ):
            return True

        return False

    # -----------------------------------------------
    # OTHER CATEGORIES
    # -----------------------------------------------

    keywords = CATEGORY_KEYWORDS.get(
        category,
        [],
    )

    return any(
        keyword.lower() in name
        for keyword in keywords
    )


def scrape_category(page, category, url):

    print()
    print(
        f"Scraping {category}..."
    )

    print(url)

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=120000,
    )

    page.wait_for_timeout(5000)

    # Scroll down to load products.
    for _ in range(8):

        page.mouse.wheel(
            0,
            2500,
        )

        page.wait_for_timeout(1200)

    links = page.locator(
        "a[href*='/p/'], "
        "a[href*='/product/']"
    )

    count = links.count()

    print(
        f"Found {count} possible product links"
    )

    products = []

    seen_urls = set()

    for i in range(count):

        try:

            link = links.nth(i)

            href = link.get_attribute(
                "href"
            )

            text = link.inner_text(
                timeout=3000
            )

            if not href or not text:
                continue

            if href.startswith("/"):
                href = (
                    "https://www.vijaysales.com"
                    + href
                )

            href = href.split("?")[0]

            if href in seen_urls:
                continue

            seen_urls.add(href)

            text = clean_text(text)

            if "₹" not in text:
                continue

            name = clean_product_name(
                text
            )

            if len(name) < 10:
                continue

            if not matches_category(
                name,
                category,
            ):
                continue

            price = extract_price(
                text
            )

            if price is None:
                continue

            product = {
                "name": name,
                "category": category,
                "price": price,
                "source_url": href,
                "retailer": "Vijay Sales",
            }

            products.append(
                product
            )

        except Exception:
            continue

    print(
        f"{category}: "
        f"{len(products)} products"
    )

    return products


def save_products(products):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            products,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(
        f"Saved: {OUTPUT_FILE}"
    )


def scrape_all_vijay_sales():

    all_products = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
        )

        page = browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            },
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 "
                "Safari/537.36"
            ),
        )

        for category, url in CATEGORIES.items():

            try:

                products = scrape_category(
                    page,
                    category,
                    url,
                )

                all_products.extend(
                    products
                )

            except Exception as e:

                print(
                    f"{category} failed: {e}"
                )

        browser.close()

    # Remove duplicate URLs.
    unique_products = []

    seen = set()

    for product in all_products:

        key = (
            product["source_url"],
            product["category"],
        )

        if key in seen:
            continue

        seen.add(key)

        unique_products.append(
            product
        )

    save_products(
        unique_products
    )

    print()
    print(
        "Total Vijay Sales products: "
        f"{len(unique_products)}"
    )

    return unique_products


if __name__ == "__main__":
    scrape_all_vijay_sales()