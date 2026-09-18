import shutil
import time
from datetime import datetime
from pathlib import Path

from app.scraper.reliance import scrape_reliance
from app.scraper.vijay_sales import scrape_all_vijay_sales
from app.scraper.croma import scrape_all_croma
from app.services.compare_snapshots import create_report
from app.services.report_generator import generate_report
from app.services.email_service import send_report


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
SNAPSHOT_DIR = DATA_DIR / "snapshots"


RELIANCE_CATEGORIES = {
    "Laptops": (
        "https://www.reliancedigital.in/collection/laptops"
    ),
    "Televisions": (
        "https://www.reliancedigital.in/sections/televisions"
    ),
    "Mobiles": (
        "https://www.reliancedigital.in/collection/"
        "mobiles/?internal_source=navigation"
    ),
    "Air Conditioners": (
        "https://www.reliancedigital.in/sections/air-conditioners"
    ),
    "Washing Machines": (
        "https://www.reliancedigital.in/sections/washing-machines"
    ),
}


def save_snapshot(
    source_file,
    retailer,
    date,
):
    destination_dir = (
        SNAPSHOT_DIR / date
    )

    destination_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = (
        destination_dir
        / f"{retailer}.json"
    )

    shutil.copy2(
        source_file,
        destination,
    )

    print(
        f"Snapshot saved: {destination}"
    )


def run_reliance():

    print("=" * 60)
    print("1. RELIANCE DIGITAL")
    print("=" * 60)

    all_products = []

    for category, category_url in RELIANCE_CATEGORIES.items():

        try:

            products = scrape_reliance(
                category,
                category_url,
            )

            all_products.extend(
                products
            )

        except Exception as e:

            print(
                f"{category} failed: {e}"
            )

    reliance_file = (
        DATA_DIR
        / "reliance_products.json"
    )

    if reliance_file.exists():

        return reliance_file

    return None


def run_daily():

    start_time = time.time()

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    start_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print("=" * 60)
    print("RELIANCE DIGITAL INTELLIGENCE")
    print("DAILY COMPETITOR MONITOR")
    print("=" * 60)

    print(
        f"Started: {start_timestamp}"
    )

    print(
        f"Snapshot date: {today}"
    )

    print()

    # -----------------------------------------
    # RELIANCE DIGITAL
    # -----------------------------------------

    try:

        reliance_file = run_reliance()

        if reliance_file:

            save_snapshot(
                reliance_file,
                "reliance",
                today,
            )

        else:

            print(
                "Reliance output file "
                "was not created."
            )

    except Exception as e:

        print(
            f"Reliance failed: {e}"
        )

    print()

    # -----------------------------------------
    # VIJAY SALES
    # -----------------------------------------

    print("=" * 60)
    print("2. VIJAY SALES")
    print("=" * 60)

    try:

        scrape_all_vijay_sales()

        vijay_file = (
            DATA_DIR
            / "vijay_sales_products.json"
        )

        if vijay_file.exists():

            save_snapshot(
                vijay_file,
                "vijay_sales",
                today,
            )

    except Exception as e:

        print(
            f"Vijay Sales failed: {e}"
        )

    print()

    # -----------------------------------------
    # CROMA
    # -----------------------------------------

    print("=" * 60)
    print("3. CROMA")
    print("=" * 60)

    try:

        scrape_all_croma()

        croma_file = (
            DATA_DIR
            / "croma_products.json"
        )

        if croma_file.exists():

            save_snapshot(
                croma_file,
                "croma",
                today,
            )

    except Exception as e:

        print(
            f"Croma failed: {e}"
        )

    print()

    # -----------------------------------------
    # COMPARE SNAPSHOTS
    # -----------------------------------------

    print("=" * 60)
    print("4. SNAPSHOT COMPARISON")
    print("=" * 60)

    comparison_created = False

    try:

        report = create_report()

        if report is None:

            print(
                "No comparison generated yet."
            )

            print(
                "A second daily snapshot "
                "is required."
            )

        else:

            comparison_created = True

            print(
                "Comparison report generated."
            )

    except Exception as e:

        print(
            f"Comparison failed: {e}"
        )

    print()

    # -----------------------------------------
    # GENERATE REPORT
    # -----------------------------------------

    print("=" * 60)
    print("5. REPORT GENERATION")
    print("=" * 60)

    report_file = None

    if comparison_created:

        try:

            report_file = generate_report()

            if report_file:

                print(
                    f"Report ready: {report_file}"
                )

            else:

                print(
                    "Report was not generated."
                )

        except Exception as e:

            print(
                f"Report generation failed: {e}"
            )

    else:

        print(
            "Email report skipped."
        )

        print(
            "A second snapshot is required."
        )

    print()

    # -----------------------------------------
    # SEND EMAIL
    # -----------------------------------------

    print("=" * 60)
    print("6. EMAIL REPORT")
    print("=" * 60)

    if report_file:

        try:

            send_report(
                report_file
            )

            print(
                "Email sent successfully."
            )

        except Exception as e:

            print(
                f"Email failed: {e}"
            )

    else:

        print(
            "Email skipped because "
            "no report was generated."
        )

    # -----------------------------------------
    # FINISH
    # -----------------------------------------

    duration = time.time() - start_time

    end_timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    print()

    print("=" * 60)
    print("DAILY RUN COMPLETE")
    print("=" * 60)

    print(
        f"Finished: {end_timestamp}"
    )

    print(
        f"Duration: "
        f"{duration / 60:.2f} minutes"
    )

    print(
        f"Snapshot: "
        f"data/snapshots/{today}/"
    )


if __name__ == "__main__":
    run_daily()