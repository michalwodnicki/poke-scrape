import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import re

from collections import defaultdict


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

BASE_URL = "https://www.pricecharting.com"

def parse_card_name(full_name: str):
    """
    Parses a PriceCharting card name.

    Example:
    'Porygon [Reverse Holo] #103a'
    ->
    base_name = 'Porygon'
    number = '103a'
    variant = 'Reverse Holo'
    """

    # extract variant inside []
    variant_match = re.search(r"\[(.*?)\]", full_name)
    variant = variant_match.group(1).strip() if variant_match else None

    # remove variant from string
    name_no_variant = re.sub(r"\s*\[.*?\]", "", full_name)

    # extract card number after #
    number_match = re.search(r"#([^\s]+)", name_no_variant)
    number = number_match.group(1) if number_match else None

    # remove number from string
    base_name = re.sub(r"\s*#[^\s]+", "", name_no_variant).strip()

    return base_name, number, variant


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
                "url": f"https://www.ebay.com/itm/{ebay_id}"
            })

    return all_sales

def scrape_pricecharting_sets():

    """
    Scrape the Pokemon card sets from PriceCharting's Pokemon category page.
    Returns a list of dicts: [{"name": ..., "url": ...}, ...]
    """

    url = "https://www.pricecharting.com/category/pokemon-cards#specific-sets"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    sets_list = []

    # PriceCharting lists Pokemon card sets under
    # a <ul> inside a "home-box all" section
    sets_block = soup.find("div", class_="home-box all")
    if not sets_block:
        return sets_list

    # Every <li><a href="...">Set Name</a></li>
    for a in sets_block.select("ul li a"):
        name = a.get_text(strip=True)
        href = a.get("href")
        if not href:
            continue

        if href and isinstance(href, str):
            full_url = urljoin(BASE_URL, href)
            sets_list.append({"name": name, "url": full_url})

    return sets_list

def scrape_pricecharting_set_cards(set_slug: str):
    """
    Scrapes all cards for a given set slug from PriceCharting using the JSON API.
    Returns a list of dicts with {"name", "url", "id"}.
    """

    cards = []
    cursor = 0

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    while True:
        params = {
            "sort": "model-number",
            "when": "none",
            "exclude-variants": "false",
            "exclude-hardware": "false",
            "cursor": cursor,
            "format": "json"
        }

        url = f"{BASE_URL}/console/{set_slug}"
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        products = data.get("products") or []

        if not products:
            # no more cards
            break

        for p in products:
            name = p.get("productName")
            uri = p.get("productUri")

            if not (name and uri):
                continue

            card_path = f"/game/{set_slug}/{uri}"
            full_url = urljoin(BASE_URL, card_path)

            cards.append({
                "name": name,
                "url": full_url,
                "id": p.get("id")
            })

        cursor += len(products)

    return cards

def card_market_prices(url: str) -> list[dict]:
        
    headers = {
    "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    soup=BeautifulSoup(resp.text, "html.parser")
    
    results=[]

    price_section = soup.find("div", id="full-prices")
    if not price_section:
        return results

    rows = price_section.select("table tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 2:
            continue
    
        grade = cols[0].get_text(strip=True)
        price_text = cols[1].get_text(strip=True)

        if price_text == "-" or not price_text:
            price = None
        else:
            price = float(
                price_text.replace("$", "").replace(",", "")
            )

        results.append({
            "grade": grade,
            "price": price
        })   

    return results

def scrape_pricecharting_card(card: dict) -> dict:
    """
    Scrapes a single card page for:
    - price guide
    - recent sales

    Input:
        card dict from your set scraper

    Returns structured card object
    """

    name = card["name"]
    url = card["url"]

    base_name, number, variant = parse_card_name(name)

    price_guide = card_market_prices(url)
    sales = scrape_pricecharting_sales(url)

    return {
        "card_id": card["id"],
        "name": card["name"],
        "base_name": base_name,
        "number": number,
        "variant": variant,

        "price_guide": price_guide,
        "sales": sales
    }
