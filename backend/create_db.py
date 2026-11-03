import os
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def run():
    url = os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@localhost:5432/ecoserve",
    )
    parsed = urlparse(url.replace("postgresql+psycopg2://", "postgresql://"))
    dbname = parsed.path.lstrip("/")

    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    if cur.fetchone():
        print(f"Database '{dbname}' already exists.")
    else:
        cur.execute(f'CREATE DATABASE "{dbname}"')
        print(f"Created database '{dbname}'.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    run()
