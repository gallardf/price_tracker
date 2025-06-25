import requests
import re
import logging

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

# Logging setup
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO,  # Change to DEBUG for even more detail
)

def get_amazon_price(url, title=None):
    logging.info(f"Scraping URL: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        logging.error(f"Request failed for {url}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    try:
        title_text = soup.find(id="productTitle").get_text(strip=True) if not title else title
    except Exception as e:
        logging.warning(f"Title not found for {url}: {e}")
        title_text = title or "Unknown"

    price_whole = soup.find("span", {"class": "a-price-whole"})
    price_fraction = soup.find("span", {"class": "a-price-fraction"})

    if not price_whole:
        logging.warning(f"No price found for {url}")
        return None

    price_text = price_whole.get_text(strip=True)
    price_fraction_text = price_fraction.get_text(strip=True) if price_fraction else "00"

    # Cleaning (removing non-breaking spaces, dots, etc.)
    price_text = re.sub(r"[^\d]", "", price_text)
    price_fraction_text = re.sub(r"[^\d]", "", price_fraction_text)

    try:
        price_float = float(f"{price_text}.{price_fraction_text}")
    except Exception as e:
        logging.error(f"Error converting price for {url}: {e} (price_text='{price_text}', price_fraction_text='{price_fraction_text}')")
        return None

    logging.info(f"Scraped: {title_text} | Price: {price_float}")
    return {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "url": url,
        "title": title_text,
        "price": price_float,
    }

def scrape_all_products():
    logging.info("=== Starting full scraping job ===")
    products = get_all_products()
    if not products:
        logging.warning("No products found in database to scrape.")
        return []

    results = []
    for product in products:
        logging.info(f"Processing product (ID={product.id}): {product.title or product.url}")
        data = get_amazon_price(product.url, product.title)
        if data:
            data['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_price(data)
            results.append({"title": product.title or data["title"], "price": data["price"], "status": "OK"})
            logging.info(f"Saved price for: {data['title']} ({data['price']})")
        else:
            results.append({"title": product.title or product.url, "price": None, "status": "FAILED"})
            logging.error(f"Failed to scrape price for: {product.title or product.url}")
    logging.info("=== Scraping job finished ===")
    return results

if __name__ == "__main__":
    logging.info("Initializing database if needed.")
    init_db()
    scrape_all_products()
