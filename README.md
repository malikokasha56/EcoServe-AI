# EcoServe AI

A decision-support web application for restaurant demand forecasting. It runs a controlled comparison of
forecasting models (LSTM, Prophet and Random Forest for daily demand; linear regression, a neural network,
Random Forest and gradient boosting for item-level demand, each against simple baselines), simulates
preparation plans built from the forecasts, flags unusual sales days and suggests preparation quantities.

- **Backend:** Flask REST API (Python), SQLAlchemy, JWT authentication
- **Database:** SQLite by default (a single file, nothing to install). PostgreSQL is optional.
- **Frontend:** React + TypeScript (Vite), served by the Flask app
- **Machine learning:** TensorFlow/Keras, Prophet, scikit-learn. Models are trained offline and their
  results are stored, so the app runs without these libraries.

## Data

All data comes from one public source: **Restaurant Sales Report 2024-2025** by Alexand Chen on Kaggle
(https://www.kaggle.com/datasets/alexandchen/restaurant-sales-report-2024-2025), licence CC BY-SA 4.0.
It holds item-level daily sales for 50 restaurants and contains no personal data, so no human participants
are involved. The dataset has no waste measurements: waste figures in the app are estimates of
overproduction derived from forecasts, and inventory figures are illustrative.

## Running the application (Windows)

1. Install **Python 3.12** from https://www.python.org/downloads/ and tick **"Add python.exe to PATH"**.
   (Python 3.9 to 3.13 all work. Skip this if Python is already installed.)
2. Double-click **`START.bat`**.

The first run takes about a minute to set up (it works offline, the required packages are included in
`backend/wheels`). Later runs start in a few seconds. The browser opens automatically at
`http://127.0.0.1:5000/` and the window shows a system check:

```
  [OK] Database       sqlite
  [OK] Sales data     10000 records
  [OK] Demo account
  [OK] Model results  15 model comparison results
  [OK] Web interface
```

**Login:** `manager@restaurant.com` / `password123`

Keep the window open while using the app. Close it (or press Ctrl+C) to stop.

- If port 5000 is busy, the next free port is used and shown in the window.
- **`RESET_DATA.bat`** restores the original dataset, removing any sales, waste entries or accounts
  added while using the app.
- **No Python available?** Open `portable\EcoServe\` and double-click **`EcoServe.exe`**. It contains
  everything and needs nothing installed.

**macOS / Linux:** run `./start.sh` from a terminal (needs Python 3.9 to 3.13).

## Checking the system

`http://127.0.0.1:5000/api/health` reports the state of the database, data, model results and web
interface as JSON.

## Development

```
cd backend
.venv\Scripts\python run.py --no-browser      # API on port 5000
npm install                                   # in the project root, once
npm run dev                                   # frontend with live reload on port 5173
npm run build                                 # rebuild dist/ which run.py serves
```

## Testing

Double-click **`RUN_TESTS.bat`** (after `START.bat` has been run once). It installs the test runner offline and
runs the automated tests against a temporary copy of the database. Without the machine learning libraries the
machine learning unit tests are skipped and reported as skipped.

The full suite (90 tests: API, machine learning and data) runs with the machine learning libraries installed:

```
cd backend
python -m pytest tests
```

Each run of the full suite writes its evidence to `docs/testing/`:

- `test_evidence.md` / `test_evidence.csv` every check with its input, expected result, observed result and outcome
- `traceability.md` every requirement (FR-01 to FR-16, NFR-01 to NFR-07) with the tests that cover it

The requirements are listed in `backend/tests/requirements_catalogue.py`.

## Retraining the models

The app serves pre-computed results from `backend/data/results.json`. To retrain, install the machine
learning libraries (Python 3.11 recommended, TensorFlow needs Windows long paths enabled) and run the
pre-compute script. It reruns the whole model comparison (about 15 minutes) and rewrites `results.json`.
It uses only the rows of the public dataset, never sales entered in the app, and keeps the previous results if it fails:

```
cd backend
.venv\Scripts\python -m pip install -r requirements-ml.txt
.venv\Scripts\python precompute.py
```

## Using PostgreSQL instead of SQLite

Install the driver with `pip install -r requirements-postgres.txt`, copy `backend/.env.example` to
`backend/.env` and set `DATABASE_URL`. `python create_db.py` creates the database; the tables and data
are created on the next start.

## Project layout

- `backend/` Flask API (`app.py`, `routes/`), data model (`models.py`), machine learning (`ml/`,
  `precompute.py`), setup (`bootstrap.py`) and launcher (`run.py`)
- `src/` React frontend; `dist/` its built version
- `restaurant_sales_data.csv` the dataset (10,000 item-level sales records, January 2024 to January 2025)
- `ATTRIBUTIONS.md` dataset and software credits
- `docs/testing/` generated test evidence and requirements traceability
- `report/` scripts that make the report figures (`make_figures.py`) and build the report from its chapters
- `portable/EcoServe/` self contained `EcoServe.exe` that runs without Python
