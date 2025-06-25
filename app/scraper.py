import os
import requests
import re
import sys

import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime

from storage import save_price, get_all_products
from models import init_db

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    )
}

def get_amazon_price(url, title=None):
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "html.parser")

    title_text = soup.find(id="productTitle").get_text(strip=True) if not title else title
    price_whole = soup.find("span", {"class": "a-price-whole"})
    price_fraction = soup.find("span", {"class": "a-price-fraction"})

    if not title_text or not price_whole:
        print("Product not found.")
        return None

    price_text = price_whole.get_text(strip=True)
    price_fraction_text = price_fraction.get_text(strip=True) if price_fraction else "00"

    # Cleaning (removing non-breaking spaces, dots, etc.)
    price_text = re.sub(r"[^\d]", "", price_text)  # keep only digits
    price_fraction_text = re.sub(r"[^\d]", "", price_fraction_text)  # same for cents

    try:
        price_float = float(f"{price_text}.{price_fraction_text}")
    except Exception as e:
        print("Error converting price:", e)
        return None

    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "title": title_text,
        "price": price_float,
    }

def scrape_all_products():
    products = get_all_products()
    results = []
    for product in products:
        data = get_amazon_price(product.url, product.title)
        if data:
            data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_price(data)
            results.append({"title": product.title or data["title"], "price": data["price"], "status": "OK"})
        else:
            results.append({"title": product.title or product.url, "price": None, "status": "FAILED"})
    return results


if __name__ == "__main__":
    init_db()
    scrape_all_products()