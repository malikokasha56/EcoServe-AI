"""Start EcoServe AI: prepares the database, checks the system and serves the app on one port."""
import argparse
import socket
import sys
import threading
import webbrowser

from bootstrap import DEMO_EMAIL, DEMO_PASSWORD


def free_port(preferred, host):
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    sys.exit(f"No free port found between {preferred} and {preferred + 19}.")


def print_checks(status):
    labels = {
        "database": "Database",
        "sales_data": "Sales data",
        "demo_user": "Demo account",
        "model_results": "Model results",
        "frontend": "Web interface",
    }
    for key, label in labels.items():
        check = status["checks"].get(key)
        if check is None:
            continue
        mark = "OK" if check["ok"] else "!!"
        detail = ""
        if key == "database" and check["ok"]:
            detail = check["engine"]
        elif key == "sales_data":
            detail = f"{check['records']} records"
        elif key == "model_results":
            detail = f"{check['results']} model comparison results" if check["results"] else "none found"
        elif key == "database":
            detail = check.get("error", "")
        print(f"  [{mark}] {label:<14} {detail}")


def main():
    parser = argparse.ArgumentParser(description="Run EcoServe AI")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    print("\n  EcoServe AI - starting\n")
    try:
        from app import create_app, system_status
        from bootstrap import ensure_ready

        app = create_app()
        with app.app_context():
            ensure_ready(log=print)
            status = system_status()
    except Exception as e:
        print(f"\n  Could not start: {e}\n")
        print("  If backend\\.env sets DATABASE_URL to PostgreSQL, check the server is running and the")
        print("  password is right, or delete backend\\.env to use the built-in SQLite database.\n")
        sys.exit(1)

    print_checks(status)
    if status["status"] == "error":
        sys.exit("\n  System check failed, see above.\n")
    if not status["checks"]["frontend"]["ok"]:
        print("\n  The web interface is not built. Run 'npm run build' or use 'npm run dev' (port 5173).")

    port = free_port(args.port, args.host)
    url = f"http://127.0.0.1:{port}/"
    print(f"\n  EcoServe AI is running at {url}")
    print(f"  Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    print("  Keep this window open while using the app. Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Timer(1.5, webbrowser.open, [url]).start()

    try:
        from waitress import serve
        serve(app, host=args.host, port=port, threads=8, _quiet=True)
    except ImportError:
        app.run(host=args.host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
