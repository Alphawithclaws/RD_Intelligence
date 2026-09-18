# RD Intelligence

### Automated Competitive Intelligence for Retail

RD Intelligence is a competitive intelligence and monitoring system built around real-time product data from major Indian electronics retailers.

The system tracks **Reliance Digital, Vijay Sales, and Croma**, collects product information, stores historical snapshots, detects changes between runs, and presents the results through an interactive dashboard.

---

## Overview

Retail pricing and product catalogues change constantly. Manually monitoring competitors across multiple categories is time-consuming and makes it difficult to identify changes quickly.

RD Intelligence automates this process by combining:

- Web scraping
- Historical snapshots
- Product-level comparison
- Price movement detection
- Automated reporting
- AI-assisted analysis
- A React dashboard

The goal is to turn raw competitor catalogue data into a structured intelligence workflow.

---

## Key Features

### Competitor Monitoring

Currently designed to monitor:

- Reliance Digital
- Vijay Sales
- Croma

The system collects available product information across categories such as:

- Laptops
- Televisions
- Air Conditioners
- Washing Machines
- Mobiles

---

### Automated Web Scraping

Product information is collected directly from retailer websites using **Playwright**.

The scraper extracts information such as:

- Product name
- Brand
- Price
- MRP
- Discount
- Rating
- Review count
- Product URL
- Category
- Scrape timestamp

---

### Historical Snapshots

Each scraping run can be stored as a timestamped snapshot.

This allows the system to compare different collection dates instead of only looking at the current catalogue.

Example:

```text
Yesterday
    ↓
Historical Snapshot
    ↓
Today's Scrape
    ↓
Comparison
