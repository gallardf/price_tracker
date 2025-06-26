from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Response
from scraper import scrape_all_products
import time

app = FastAPI()

# Define metrics
SCRAP_SUCCESS = Counter('scrap_success_total', 'Number of successful scrap')
SCRAP_FAILED = Counter('scrap_failed_total', 'Number of failed scrap')
SCRAP_DURATION = Histogram('scrap_duration_seconds', 'Scraping duration in seconds')

@app.post("/scrape")
def run_scraper():
    start = time.time()
    results = scrape_all_products()
    duration = time.time() - start

    # Update metrics
    failed = sum(1 for r in results if r.get('status') == 'FAILED')
    success = sum(1 for r in results if r.get('status') == 'OK')

    SCRAP_SUCCESS.inc(success)
    SCRAP_FAILED.inc(failed)
    SCRAP_DURATION.observe(duration)

    return {"results": results, "success": success, "failed": failed, "duration": duration}

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
