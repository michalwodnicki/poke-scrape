from flask import Blueprint, render_template, request

from .services.ebay import search_items

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
    results = None
    query = ""
    
    print("Request method:", request.method)

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            try:
                results = search_items(query)
            except Exception as e:
                print("Error fetching from eBay:", e)
                results = []

    return render_template("search.html", query=query, results=results)