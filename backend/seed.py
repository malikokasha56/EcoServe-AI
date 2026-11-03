# Kept for compatibility: database setup now lives in bootstrap.py and also runs automatically from run.py.
from app import create_app
from bootstrap import ensure_ready, DEMO_EMAIL, DEMO_PASSWORD

if __name__ == "__main__":
    with create_app().app_context():
        ensure_ready()
        print(f"\nDemo login -> email: {DEMO_EMAIL}  password: {DEMO_PASSWORD}")
