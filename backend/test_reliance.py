from app.scraper.reliance import scrape_reliance


if __name__ == "__main__":
    scrape_reliance(
        "https://www.reliancedigital.in/",
        limit=30
    )