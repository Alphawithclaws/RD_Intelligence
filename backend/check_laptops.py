from playwright.sync_api import sync_playwright


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={
            "width": 1440,
            "height": 900
        }
    )

    page.goto(
        "https://www.reliancedigital.in/sections/laptops",
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(7000)

    # Scroll gradually so lazy-loaded products appear
    for _ in range(10):
        page.mouse.wheel(0, 1500)
        page.wait_for_timeout(1000)

    print()
    print("=" * 60)
    print("PAGE TEXT")
    print("=" * 60)

    text = page.locator("body").inner_text()

    print(text[:12000])

    print()
    print("=" * 60)
    print("LINKS CONTAINING LAPTOP / DELL / HP / LENOVO / ASUS")
    print("=" * 60)

    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(a => ({
            text: a.innerText.trim(),
            href: a.href
        })).filter(x => x.text && x.href)
        """
    )

    keywords = [
        "laptop",
        "dell",
        "hp ",
        "lenovo",
        "asus",
        "acer",
        "apple macbook",
        "macbook",
        "msi"
    ]

    found = []

    for item in links:

        text_lower = item["text"].lower()

        if any(keyword in text_lower for keyword in keywords):

            if item not in found:
                found.append(item)

    for item in found:

        print()
        print("TEXT:", item["text"].replace("\n", " ")[:250])
        print("URL :", item["href"])

    print()
    print("=" * 60)
    print("TOTAL MATCHES:", len(found))
    print("=" * 60)

    browser.close()