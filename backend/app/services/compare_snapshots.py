import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parents[2]

SNAPSHOT_DIR = BASE_DIR / "data" / "snapshots"
REPORT_DIR = BASE_DIR / "data" / "reports"


RETAILERS = [
    "reliance",
    "vijay_sales",
    "croma",
]


def load_json(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def get_snapshot_dates():

    if not SNAPSHOT_DIR.exists():
        return []

    dates = []

    for folder in SNAPSHOT_DIR.iterdir():

        if not folder.is_dir():
            continue

        try:

            datetime.strptime(
                folder.name,
                "%Y-%m-%d",
            )

            dates.append(folder.name)

        except ValueError:
            continue

    return sorted(dates)


def compare_products(
    yesterday,
    today,
):

    yesterday_map = {
        product.get("source_url"): product
        for product in yesterday
        if product.get("source_url")
    }

    today_map = {
        product.get("source_url"): product
        for product in today
        if product.get("source_url")
    }

    new_products = []
    removed_products = []
    price_changes = []

    # -----------------------------------------
    # NEW + PRICE CHANGES
    # -----------------------------------------

    for url, product in today_map.items():

        if url not in yesterday_map:

            new_products.append(product)

            continue

        old_product = yesterday_map[url]

        old_price = old_product.get("price")
        new_price = product.get("price")

        if (
            old_price is not None
            and new_price is not None
            and old_price != new_price
        ):

            difference = (
                new_price - old_price
            )

            if old_price != 0:

                percentage = (
                    difference
                    / old_price
                    * 100
                )

            else:

                percentage = None

            price_changes.append(
                {
                    "name": product.get(
                        "product_name"
                    ) or product.get("name"),

                    "category": product.get(
                        "category"
                    ),

                    "old_price": old_price,

                    "new_price": new_price,

                    "difference": difference,

                    "percentage": percentage,

                    "source_url": url,
                }
            )

    # -----------------------------------------
    # REMOVED PRODUCTS
    # -----------------------------------------

    for url, product in yesterday_map.items():

        if url not in today_map:

            removed_products.append(
                product
            )

    return {
        "new_products": new_products,
        "removed_products": removed_products,
        "price_changes": price_changes,
    }


def compare_retailer(
    retailer,
    yesterday_date,
    today_date,
):

    yesterday_file = (
        SNAPSHOT_DIR
        / yesterday_date
        / f"{retailer}.json"
    )

    today_file = (
        SNAPSHOT_DIR
        / today_date
        / f"{retailer}.json"
    )

    if not yesterday_file.exists():

        return {
            "retailer": retailer,
            "status": "missing_yesterday",
        }

    if not today_file.exists():

        return {
            "retailer": retailer,
            "status": "missing_today",
        }

    yesterday = load_json(
        yesterday_file
    )

    today = load_json(
        today_file
    )

    # -----------------------------------------
    # SOURCE UNAVAILABLE
    #
    # An empty scrape does NOT automatically
    # mean that every previous product vanished.
    # -----------------------------------------

    if (
        retailer == "croma"
        and len(today) == 0
    ):

        return {
            "retailer": retailer,
            "status": "source_unavailable",
            "yesterday_count": len(yesterday),
            "today_count": None,
            "new_products": [],
            "removed_products": [],
            "price_changes": [],
        }

    comparison = compare_products(
        yesterday,
        today,
    )

    return {
        "retailer": retailer,
        "status": "ok",
        "yesterday_count": len(yesterday),
        "today_count": len(today),
        **comparison,
    }


def create_report():

    dates = get_snapshot_dates()

    if len(dates) < 2:

        print(
            "Need at least two snapshot dates "
            "to compare."
        )

        return None

    yesterday_date = dates[-2]
    today_date = dates[-1]

    print()

    print(
        f"Comparing {yesterday_date} "
        f"vs {today_date}"
    )

    retailers = {}

    for retailer in RETAILERS:

        print(
            f"Comparing {retailer}..."
        )

        retailers[retailer] = (
            compare_retailer(
                retailer,
                yesterday_date,
                today_date,
            )
        )

    report = {
        "generated_at": (
            datetime.now().isoformat()
        ),

        "yesterday": yesterday_date,

        "today": today_date,

        "retailers": retailers,
    }

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_file = (
        REPORT_DIR
        / f"report_{today_date}.json"
    )

    with open(
        report_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            report,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()

    print(
        f"Report saved: {report_file}"
    )

    print()

    print("SUMMARY")

    print("=" * 50)

    for retailer, data in retailers.items():

        print()

        print(
            retailer.upper()
        )

        if data["status"] != "ok":

            print(
                f"Status: "
                f"{data['status']}"
            )

            if data.get(
                "yesterday_count"
            ) is not None:

                print(
                    f"Yesterday: "
                    f"{data['yesterday_count']}"
                )

            print(
                "Today: unavailable"
            )

            print(
                "New products: —"
            )

            print(
                "Removed products: —"
            )

            print(
                "Price changes: —"
            )

            continue

        print(
            f"Yesterday: "
            f"{data['yesterday_count']}"
        )

        print(
            f"Today: "
            f"{data['today_count']}"
        )

        print(
            f"New products: "
            f"{len(data['new_products'])}"
        )

        print(
            f"Removed products: "
            f"{len(data['removed_products'])}"
        )

        print(
            f"Price changes: "
            f"{len(data['price_changes'])}"
        )

    return report


if __name__ == "__main__":

    create_report()