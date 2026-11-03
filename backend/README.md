# EcoServe AI - Backend

Flask REST API. See the main `README.md` in the project root for how to run the application.

- `run.py` launcher: prepares the database, runs a system check, serves the API and the built frontend
- `bootstrap.py` creates the tables, loads `restaurant_sales_data.csv`, the demo user, the inventory
  and the pre-computed model results from `data/results.json` (idempotent, runs on every start)
- `precompute.py` runs the controlled comparison and the preparation simulation and stores every result,
  then rewrites `data/results.json` (needs `requirements-ml.txt`; uses only the dataset rows)
- `app.py` application factory, health check, error handling, frontend serving
- `routes/` one blueprint per area (auth, sales, waste, forecast, simulation, recommendations, anomalies,
  dashboard, inventory, reports, public)
- `ml/experiment.py` the two comparison tracks (daily: mean, seasonal naive, Prophet, LSTM, Random Forest;
  item level: mean, historical average, linear regression, neural network, Random Forest, gradient boosting)
  and the Diebold-Mariano test
- `ml/simulation.py` the preparation simulation, `ml/anomaly.py` the Z score and IQR rules,
  `ml/forecasting.py` shared metrics
- `tests/` automated tests (`python -m pytest tests`), requirements catalogue and evidence recorder
- `wheels/` offline copies of the runtime packages used by `START.bat`

Requirements are split so the app itself stays light:

- `requirements.txt` runtime only
- `requirements-dev.txt` adds pytest for the automated tests
- `requirements-ml.txt` adds the libraries needed to retrain the models
- `requirements-postgres.txt` adds the PostgreSQL driver
