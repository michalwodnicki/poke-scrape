from flask import Blueprint, render_template, request
from urllib.parse import quote

from app.services.ebay import search_items
from app.services.pricecharting import scrape_pricecharting_sales, compute_comp_stats


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("home.html")


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact")
def contact():
    return render_template("contact.html")


@main.route("/search", methods=["GET", "POST"])
def search():
    query = ""
    sales = []
    stats = {}

    if request.method == "POST":
        raw_url = request.form.get("url", "").strip()

        if raw_url:
            url = raw_url  # use whatever the user pasted
            sales = scrape_pricecharting_sales(url)
            sales = sorted(sales, key=lambda x: x["date"], reverse=True)
            stats = compute_comp_stats(sales)
            query = raw_url  # so we display the URL back in the template

    return render_template(
        "search.html",
        query=query,
        results=sales,
        stats=stats
    )