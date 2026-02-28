import requests
from bs4 import BeautifulSoup
from datetime import datetime

from collections import defaultdict
import statistics


GRADE_MAP = {
    "completed-auctions-used": "Ungraded",
    "completed-auctions-grade-nineteen": "CGC 10 Prist.",
    "completed-auctions-manual-only": "PSA 10",
    "completed-auctions-grade-seventeen": "CGC 10",
    "completed-auctions-grade-twenty-one": "TAG 10",
    "completed-auctions-grade-twenty-two": "ACE 10",
    "completed-auctions-box-only": "Grade 9.5",
    "completed-auctions-graded": "Grade 9",
    "completed-auctions-new": "Grade 8",
    "completed-auctions-cib": "Grade 7",
    "completed-auctions-grade-six": "Grade 6",
    "completed-auctions-grade-five": "Grade 5",
    "completed-auctions-grade-four": "Grade 4",
    "completed-auctions-grade-three": "Grade 3",
    "completed-auctions-box-and-manual": "Grade 2",
    "completed-auctions-loose-and-manual": "Grade 1",
}


def scrape_pricecharting_sales(url: str) -> list[dict]:
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    all_sales: list[dict] = []

    containers = soup.select("div[class*='completed-auctions-']")

    for container in containers:
        class_list = container.get("class") or []

        container_class = next(
            (c for c in class_list if c.startswith("completed-auctions-")),
            None
        )

        if not container_class:
            continue

        grade_label = GRADE_MAP.get(container_class)
        if not grade_label:
            continue

        rows = container.select("tr[id^='ebay-']")
        if not rows:
            continue

        for row in rows:
            title_tag = row.find("td", class_="title")
            price_tag = row.find("span", class_="js-price")
            date_tag = row.find("td", class_="date")

            if not (title_tag and price_tag and date_tag):
                continue

            ebay_id = str(row["id"]).replace("ebay-", "")

            price_text = (
                price_tag.get_text(strip=True)
                .replace("$", "")
                .replace(",", "")
            )

            try:
                price = float(price_text)
            except ValueError:
                continue

            try:
                date = datetime.strptime(
                    date_tag.get_text(strip=True),
                    "%Y-%m-%d"
                )
            except ValueError:
                continue

            all_sales.append({
                "ebay_id": ebay_id,
                "grade": grade_label,
                "date": date,
                "price": price,
                "title": title_tag.get_text(strip=True),
            })

    return all_sales

def compute_comp_stats(sales: list[dict]) -> dict:
    """
    Accepts list of sale dictionaries.
    Returns grade-level summary statistics.
    """

    if not sales:
        return {}

    grade_groups: dict[str, list[dict]] = defaultdict(list)

    # Group sales by grade
    for sale in sales:
        grade_groups[sale["grade"]].append(sale)

    summary = {}

    for grade, items in grade_groups.items():
        prices = [item["price"] for item in items]

        # Most recent sale (based on datetime object in "date")
        latest_sale_price = max(
            items,
            key=lambda x: x["date"]
        )["price"]

        summary[grade] = {
            "count": len(prices),
            "median": round(statistics.median(prices), 2),
            "mean": round(statistics.mean(prices), 2),
            "min": min(prices),
            "max": max(prices),
            "latest_sale": latest_sale_price,
        }

    return summary
