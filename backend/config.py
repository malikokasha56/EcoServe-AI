import os
import secrets
import sys
from datetime import timedelta

from dotenv import load_dotenv

if getattr(sys, "frozen", False):
    # Portable EcoServe.exe: bundled files live in the unpacked bundle, the database next to the exe.
    PROJECT_DIR = sys._MEIPASS
    BASE_DIR = os.path.join(PROJECT_DIR, "backend")
    INSTANCE_DIR = os.path.join(os.path.dirname(sys.executable), "instance")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(BASE_DIR)
    INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIST = os.path.join(PROJECT_DIR, "dist")
CSV_PATH = os.path.join(PROJECT_DIR, "restaurant_sales_data.csv")
RESULTS_PATH = os.path.join(DATA_DIR, "results.json")
SQLITE_PATH = os.path.join(INSTANCE_DIR, "ecoserve.db")

load_dotenv(os.path.join(BASE_DIR, ".env"))

# The only data source: a public secondary dataset with no personal data, so no human participants are involved.
DATASET = {
    "title": "Restaurant Sales Report 2024-2025",
    "author": "Alexand Chen",
    "publisher": "Kaggle",
    "url": "https://www.kaggle.com/datasets/alexandchen/restaurant-sales-report-2024-2025",
    "licence": "CC BY-SA 4.0",
    "file": "restaurant_sales_data.csv",
    "description": "Public item-level daily sales for 50 restaurants (14 menu items), January 2024 to "
                   "January 2025, with price, promotion, event and weather fields. Contains no personal data.",
}
os.makedirs(INSTANCE_DIR, exist_ok=True)


# Secrets come from the environment if set, otherwise a random value is generated once
# and kept in the instance folder so logins survive a restart.
def _secret(name):
    value = os.environ.get(name)
    if value:
        return value
    path = os.path.join(INSTANCE_DIR, f"{name.lower()}.txt")
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(secrets.token_hex(32))
    with open(path) as f:
        return f.read().strip()


class Config:
    SECRET_KEY = _secret("SECRET_KEY")
    JWT_SECRET_KEY = _secret("JWT_SECRET_KEY")

    # NFR-UM-03: sessions expire after 30 minutes of inactivity (tokens are refreshed while in use)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)

    # SQLite by default so the system runs with no database server; set DATABASE_URL to use PostgreSQL.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + SQLITE_PATH.replace("\\", "/")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    INSTANCE_DIR = INSTANCE_DIR

    # Restaurant this single-tenant deployment serves
    DEFAULT_RESTAURANT_ID = 1

    # FR-RC-01: preparation recommendation safety factor default 10%
    SAFETY_FACTOR = 0.10
