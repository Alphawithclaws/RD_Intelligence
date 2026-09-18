from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Reliance Digital Intelligence API"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"


@app.get("/")
def home():
    return {
        "message": "Reliance Digital Intelligence API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/dashboard")
def dashboard():

    result = {}

    files = {
        "reliance": "reliance_products.json",
        "vijay_sales": "vijay_sales_products.json",
        "croma": "croma_products.json",
    }

    for retailer, filename in files.items():

        file_path = DATA_DIR / filename

        if file_path.exists():

            with open(
                file_path,
                "r",
                encoding="utf-8",
            ) as f:
                products = json.load(f)

            result[retailer] = {
                "count": len(products),
                "products": products,
            }

        else:

            result[retailer] = {
                "count": 0,
                "products": [],
            }

    return result


@app.get("/price-movements")
def price_movements():

    reports = sorted(
        REPORTS_DIR.glob("report_*.json"),
        reverse=True,
    )

    if not reports:

        return {
            "available": False,
            "message": "No comparison report available yet.",
            "report": None,
        }

    latest_report = reports[0]

    with open(
        latest_report,
        "r",
        encoding="utf-8",
    ) as f:
        report = json.load(f)

    return {
        "available": True,
        "report": report,
    }


@app.get("/reports")
def reports():

    report_files = sorted(
        REPORTS_DIR.glob("daily_report_*.html"),
        reverse=True,
    )

    comparison_files = sorted(
        REPORTS_DIR.glob("report_*.json"),
        reverse=True,
    )

    return {
        "daily_reports": [
            {
                "name": file.name,
                "date": file.stem.replace(
                    "daily_report_",
                    "",
                ),
            }
            for file in report_files
        ],
        "comparison_reports": [
            {
                "name": file.name,
                "date": file.stem.replace(
                    "report_",
                    "",
                ),
            }
            for file in comparison_files
        ],
    }