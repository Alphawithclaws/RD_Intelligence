import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"
REPORT_DIR = DATA_DIR / "reports"


def load_latest_report():
    reports = sorted(
        REPORT_DIR.glob("report_*.json")
    )

    if not reports:
        return None

    latest = reports[-1]

    with open(
        latest,
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def format_price(value):
    if value is None:
        return "N/A"

    try:
        return f"₹{float(value):,.0f}"
    except:
        return str(value)


def generate_html_report(report):
    if not report:
        return None

    report_date = report.get(
        "date",
        datetime.now().strftime("%Y-%m-%d"),
    )

    previous_date = report.get(
        "previous_date",
        "Previous snapshot",
    )

    changes = report.get(
        "changes",
        {},
    )

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                margin: 0;
                padding: 30px;
                color: #222;
            }}

            .container {{
                max-width: 900px;
                margin: auto;
                background: white;
                padding: 35px;
                border-radius: 12px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            .date {{
                color: #777;
                margin-bottom: 30px;
            }}

            .retailer {{
                border-top: 1px solid #ddd;
                padding-top: 25px;
                margin-top: 25px;
            }}

            .stats {{
                display: flex;
                gap: 15px;
                margin: 15px 0;
            }}

            .stat {{
                background: #f3f3f3;
                padding: 15px;
                border-radius: 8px;
                flex: 1;
            }}

            .stat-number {{
                font-size: 24px;
                font-weight: bold;
            }}

            .change {{
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }}

            .price {{
                font-weight: bold;
            }}

            .footer {{
                margin-top: 35px;
                color: #888;
                font-size: 13px;
            }}

        </style>

    </head>

    <body>

        <div class="container">

            <h1>
                Reliance Digital Intelligence
            </h1>

            <div class="date">
                Daily Competitor Report
                <br>
                {report_date}
                vs
                {previous_date}
            </div>
    """

    for retailer, retailer_data in changes.items():

        new_products = retailer_data.get(
            "new_products",
            [],
        )

        removed_products = retailer_data.get(
            "removed_products",
            [],
        )

        price_changes = retailer_data.get(
            "price_changes",
            [],
        )

        html += f"""
            <div class="retailer">

                <h2>
                    {retailer.replace("_", " ").title()}
                </h2>

                <div class="stats">

                    <div class="stat">
                        <div class="stat-number">
                            {len(new_products)}
                        </div>
                        New Products
                    </div>

                    <div class="stat">
                        <div class="stat-number">
                            {len(removed_products)}
                        </div>
                        Removed
                    </div>

                    <div class="stat">
                        <div class="stat-number">
                            {len(price_changes)}
                        </div>
                        Price Changes
                    </div>

                </div>
        """

        if price_changes:

            html += "<h3>Price Changes</h3>"

            for change in price_changes:

                product_name = change.get(
                    "name",
                    "Unknown Product",
                )

                old_price = change.get(
                    "old_price"
                )

                new_price = change.get(
                    "new_price"
                )

                html += f"""
                    <div class="change">

                        <strong>
                            {product_name}
                        </strong>

                        <br>

                        <span class="price">
                            {format_price(old_price)}
                            →
                            {format_price(new_price)}
                        </span>

                    </div>
                """

        if new_products:

            html += "<h3>New Products</h3>"

            for product in new_products[:20]:

                if isinstance(product, dict):
                    name = product.get(
                        "name",
                        "Unknown Product",
                    )
                else:
                    name = str(product)

                html += f"""
                    <div class="change">
                        {name}
                    </div>
                """

        if removed_products:

            html += "<h3>Removed Products</h3>"

            for product in removed_products[:20]:

                if isinstance(product, dict):
                    name = product.get(
                        "name",
                        "Unknown Product",
                    )
                else:
                    name = str(product)

                html += f"""
                    <div class="change">
                        {name}
                    </div>
                """

        if not (
            new_products
            or removed_products
            or price_changes
        ):

            html += """
                <p>
                    No changes detected.
                </p>
            """

        html += """
            </div>
        """

    html += """

            <div class="footer">
                Generated automatically by
                Reliance Digital Intelligence.
            </div>

        </div>

    </body>
    </html>
    """

    return html


def save_html_report(html, date):
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        REPORT_DIR
        / f"daily_report_{date}.html"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(html)

    return output_file


def generate_report():

    report = load_latest_report()

    if not report:
        print(
            "No comparison report found."
        )
        return None

    date = report.get(
        "date",
        datetime.now().strftime("%Y-%m-%d"),
    )

    html = generate_html_report(
        report
    )

    output_file = save_html_report(
        html,
        date,
    )

    print(
        f"Email report generated: "
        f"{output_file}"
    )

    return output_file


if __name__ == "__main__":
    generate_report()