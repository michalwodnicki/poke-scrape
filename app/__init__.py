from flask import Flask, render_template, request

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route("/contact")
    def contact():
        return render_template("contact.html")
    
    @app.route("/search", methods=["GET", "POST"])
    def search():
        results = None
        query = ""
    
        if request.method == "POST":
            query = request.form.get("query", "").strip()
            if query:  # only create results if query is not empty
                results = [
                    {"title": f"{query} Card Example 1", "price": "20", "currency": "USD"},
                    {"title": f"{query} Card Example 2", "price": "35", "currency": "USD"},
                ]
    
        return render_template("search.html", query=query, results=results)

    return app