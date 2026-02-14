# Pokémon Price Tracker

A simple Flask web app to search for Pokémon card prices.  
Currently uses mock data; later it can be connected to the eBay API and a database to track prices over time.

---

## **Project Structure**

```
poke-scrape
├─ app
│  ├─ routes.py
│  ├─ templates
│  │  ├─ about.html
│  │  ├─ base.html
│  │  ├─ contact.html
│  │  ├─ home.html
│  │  └─ search.html
│  └─ __init__.py
├─ poetry.lock
├─ pyproject.toml
├─ README.md
└─ run.py

```

---

## Getting Started

Follow these steps to run the app locally.

### 1. Clone the repository

```bash
git clone https://github.com/michalwodnicki/poke-scrape.git
cd poke-scrape
```
### 2. Poetry Setup

Check installation: 

```bash
poetry --version
```

Install dependencies:
```bash
poetry install
```

### 3. Run the app locally

Activate the Poetry shell:
```bash
poetry shell
```

Run the Flask app:
```bash
python run.py
```

You should see output like:
Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

### 4. Using the app

- Navigate to /search to access the Pokémon card search page.
- Enter a card name (e.g., "Charizard PSA 10") and submit.
- Currently displays mock results; real eBay API integration coming soon.