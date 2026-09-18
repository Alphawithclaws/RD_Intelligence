from datetime import datetime
from pathlib import Path
import json

import requests


OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "croma_products.json"
)


CATEGORIES = {
    "Laptops": "https://www.croma.com/laptops/c/20",
    "Televisions": "https://www.croma.com/televisions/c/5",
    "Mobiles": "https://www.croma.com/mobiles/c/1",
    "Washing Machines": "https://www.croma.com/washing-machines/c/10",
}


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,"
              "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def scrape_croma(category, category_url):

    print()
    print("=" * 60)
    print(f"CROMA — {category}")
    print("=" * 60)
    print(f"Source: {category_url}")

    try:
        response = requests.get(
            category_url,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code != 200:
            print(
                f"Croma returned HTTP "
                f"{response.status_code}"
            )

            return []

        print(
            "Croma page received, "
            "but product extraction is disabled "
            "until a reliable product source is available."
        )

        return []

    except requests.RequestException as error:

        print(
            f"Croma request failed: {error}"
        )

        return []


def save_products(products):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            products,
            file,
            indent=2,
            ensure_ascii=False
        )

    print()
    print(
        f"Total Croma products: "
        f"{len(products)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )


def scrape_all_croma():

    all_products = []

    for category, url in CATEGORIES.items():

        products = scrape_croma(
            category,
            url
        )

        all_products.extend(
            products
        )

    save_products(
        all_products
    )

    return all_products


if __name__ == "__main__":

    scrape_all_croma()