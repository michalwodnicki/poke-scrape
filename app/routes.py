from flask import Blueprint, render_template, request

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

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            results = [
                {"title": f"{query} Card Example 1", "price": "20", "currency": "USD"},
                {"title": f"{query} Card Example 2", "price": "35", "currency": "USD"},
            ]

    return render_template("search.html", query=query, results=results)