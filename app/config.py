import os

from sqlalchemy.engine import URL

DB_URL = URL.create(
    "postgresql",
    username=os.getenv("DB_USERNAME"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432),
    database=os.getenv("DB_NAME")
)
