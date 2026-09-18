from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(
        "https://www.reliancedigital.in/sections/laptops",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(a => ({
            text: a.innerText.trim(),
            href: a.href
        })).filter(x => x.href.includes("/product/"))
        """
    )

    print()
    print("=" * 50)
    print("PRODUCT LINKS:", len(links))
    print("=" * 50)

    for item in links:
        print()
        print(item["text"].replace("\\n", " ")[:150])
        print(item["href"])

    browser.close()