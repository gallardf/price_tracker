from fastapi import FastAPI
from scraper import scrape_all_products

app = FastAPI()

@app.post("/scrape")
def run_scraper():
    results = scrape_all_products()
    return {"results": results}
