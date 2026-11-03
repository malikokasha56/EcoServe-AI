# 5 Implementation

## 5.1 Introduction

This chapter explains how the design was built, covering the technologies, code structure, start up and deployment, the server, the forecasting pipeline, the interface and the main problems found. Short pieces of code are shown where a decision affects the validity of the results.

## 5.2 Technology stack

The technologies were chosen because they are mature, well documented and suit a single developer. Table 5.1 lists them.

Table 5.1 Technology stack

| Layer | Technology | Role |
|---|---|---|
| Interface | React 18, TypeScript, Vite 6, Tailwind CSS 4, Recharts | Pages, charts and styling, compiled to static files |
| Server | Python 3.11, Flask 3.0, Flask JWT Extended, Flask Bcrypt, Waitress | REST interface, authentication, password hashing, production web server |
| Data | SQLAlchemy 2.0, SQLite (PostgreSQL optional) | Object relational mapping and storage |
| Forecasting | pandas, NumPy, SciPy, scikit learn 1.5, TensorFlow 2.16, Prophet 1.1.5 | Data preparation, models, statistical tests |
| Testing | pytest 8.3 | Automated tests and evidence generation |
| Packaging | Batch launcher, offline package folder, PyInstaller | One click start and a self contained executable |

The forecasting models are built with scikit learn (Pedregosa et al., 2011), TensorFlow (Abadi et al., 2016) and Prophet (Taylor and Letham, 2018). These libraries are needed only by the offline pipeline. The application itself needs nine small Python packages, stored in the project folder so it installs without an internet connection.

## 5.3 Project structure

The code is organised so each job lives in one place.

```
EcoServe AI/
  START.bat, start.sh             one click start (Windows, macOS or Linux)
  RUN_TESTS.bat, RESET_DATA.bat   run the tests, restore the demo data
  restaurant_sales_data.csv       public dataset (unmodified)
  src/                            React interface
  dist/                           compiled interface served by Flask
  backend/
    run.py                        launcher: checks, free port, server
    app.py                        application factory, errors, health check
    bootstrap.py                  builds the database from CSV and results
    models.py                     database tables
    routes/                       one module per area of the API
    ml/                           experiment, simulation, anomaly, metrics
    precompute.py                 offline pipeline, writes data/results.json
    tests/                        automated tests, requirements catalogue
    wheels/                       offline copies of the runtime packages
  portable/EcoServe/              self contained EcoServe.exe
  docs/testing/                   generated test evidence
```

## 5.4 Start up and deployment

Reliable start up was the first requirement. A system that cannot be shown cannot be assessed. The launcher, START.bat, is the only file a user opens. On the first run it finds a suitable Python installation, creates an isolated environment in the project folder and installs the bundled runtime packages. It uses the internet only if the Python version is not covered. On later runs it checks that the environment still works, which matters if the folder was copied from another computer.

The launcher then runs run.py, which prepares the database and checks the system before serving it. Figure 5.1 shows a first start on a computer where the application had never run. The database is created from the CSV and results files, five checks are reported, a free port is chosen and the browser opens.

![Figure 5.1 First start of the application, with the system checks reported by the launcher](figures/term_start.png)

Other steps make the start reliable. The SQLite database needs no server, password or settings. Secret keys are created on first start. If port 5000 is in use, the next free port is chosen. Flask serves the compiled interface through Waitress, so Node.js is not needed. RESET_DATA.bat restores the original data after a demonstration. The application is also packaged with PyInstaller as EcoServe.exe, which runs on Windows with nothing installed. Every path was tested on a clean copy of the project in a folder with spaces in its name, which often cause failure on Windows.

## 5.5 Server

An application factory creates the server. It registers one blueprint per area of the interface, sets up authentication and error handling, and adds a health check and a route that serves the compiled interface. Three details matter.

The first detail is input checking. A small helper checks number inputs and raises a validation error with a readable message, which a central handler turns into a 400 response. So a quantity of "two" or a negative number gets a clear message, not a server error. Unknown API paths return a JSON 404. Unexpected errors are logged and returned as JSON.

The second detail is session handling. Tokens expire after 30 minutes, which protects an unattended session. But an active user should not be signed out in the middle of a task. So the server issues a new token whenever a signed in request arrives with a token expiring within 15 minutes. The interface stores it automatically.

```python
@app.after_request
def refresh_expiring_token(response):
    try:
        exp = datetime.fromtimestamp(get_jwt()["exp"], timezone.utc)
        if exp - datetime.now(timezone.utc) < timedelta(minutes=15):
            response.headers["X-Refreshed-Token"] = create_access_token(identity=get_jwt_identity())
    except (RuntimeError, KeyError):
        pass
    return response
```

The third detail is that training is kept apart from serving. The retraining endpoint trains nothing itself. It checks that the machine learning libraries are installed and refuses with a reason if they are not, or if a run is already going on. Otherwise it starts the offline pipeline as a separate process, so the server keeps responding.

## 5.6 Building the database

The bootstrap module builds the database on first start and checks it on every start. It loads the 10,000 sales rows from the CSV file, creates the demo account with a bcrypt password hash, makes the example inventory from the most common ingredient tags and loads the stored model results. Every step checks whether its data already exist, so it is safe to run repeatedly. The offline pipeline uses the same module in reverse to write the results file.

## 5.7 Forecasting pipeline

The pipeline in precompute.py runs the two comparison tracks, the reference result, the simulation and the anomaly detection, and stores everything. A full run takes five to twenty minutes on a laptop, mostly spent training the LSTM for the main split and the four rolling windows in both information sets.

The most important lines for the validity of Track B compute the history feature, the average earlier sales of the same item at the same restaurant. Sales are first summed per restaurant, item and day, and a running total over days is taken. The current day's own values are removed before averaging, so the feature for a given day never includes that day or any later day.

```python
per_day = d.groupby(key + ["date"])["quantity_sold"].agg(["sum", "count"]).reset_index()
per_day[["cum_sum", "cum_n"]] = per_day.groupby(key)[["sum", "count"]].cumsum().values
per_day["prior_count"] = per_day["cum_n"] - per_day["count"]
per_day["prior_mean"] = (per_day["cum_sum"] - per_day["sum"]) / per_day["prior_count"].replace(0, np.nan)
```

The significance test is written directly from its definition, so its behaviour can be checked. The loss differential is the difference between the absolute errors of two models on each test observation. At item level, these are summed per day. The statistic, its mean divided by its standard error, is scaled by the small sample correction and compared with the t distribution.

```python
def diebold_mariano(actual, pred_a, pred_b, groups=None):
    d = np.abs(actual - pred_a) - np.abs(actual - pred_b)
    if groups is not None:
        d = pd.Series(d).groupby(groups).sum().to_numpy()
    n, var = len(d), np.mean((d - d.mean()) ** 2)
    if n < 3 or var == 0:
        return None
    stat = d.mean() / np.sqrt(var / n) * np.sqrt((n - 1) / n)
    return float(2 * stats.t.sf(abs(stat), df=n - 1))
```

The simulation is just as direct. For a given forecast and margin, three lines of array arithmetic give the quantity prepared, overproduction, unmet demand and share of demand served. This makes it easy to check by hand, as Chapter 6 shows.

```python
prepared = forecast * (1 + margin)
over = np.maximum(prepared - actual, 0)
short = np.maximum(actual - prepared, 0)
served = np.minimum(prepared, actual)
```

All models use a fixed random seed. A small change lets Prophet's precompiled model run without a separate compiler.

## 5.8 User interface

The interface has fifteen pages grouped in a sidebar. Every page gets its data through a shared hook that handles loading and error states consistently, so a failed request shows a clear message, not a blank page.

The public landing page (Figure 5.2) describes the system and shows the measured results of both comparison tracks, credits the dataset and states the limits of the work. All this is read from the server, so it cannot drift from the stored results.

![Figure 5.2 Landing page with the measured results and the data source](figures/app_landing.png)

The dashboard (Figure 5.3) summarises the latest day in the data. It shows the best daily model's forecast for that day, the error of every daily model and simulated overproduction for the last seven test days.

![Figure 5.3 Dashboard](figures/app_dashboard.png)

The model comparison page (Figure 5.4) is the centre of the application. It opens with key findings generated from the results, followed by tabs for the daily total track, the item level track, the method and the average demand per menu item. The tables mark the lowest error, show rolling origin results and p values, and keep the reference result separate from the forecasts.

![Figure 5.4 Model comparison page, daily total track](figures/app_comparison.png)

The preparation simulation page (Figure 5.5) presents the two headline comparisons with their confidence intervals. A slider compares both plans at any margin from 0 to 20 per cent. It has charts of overproduction against margin and of the trade off between overproduction and service, and lists the assumptions.

![Figure 5.5 Preparation simulation page](figures/app_simulation.png)

The preparation plan page (Figure 5.6) shows the suggested quantity of each menu item for any test day, next to what the historical average rule would have suggested and what was actually sold. It also summarises how often each plan was closer to actual sales over the whole test period.

![Figure 5.6 Preparation plan page](figures/app_plan.png)

## 5.9 Problems encountered

Several problems came up during development, and how they were handled shaped the final system.

The interface had been generated with utility classes written for an older version of the Tailwind styling library, which produced no styles with the installed version. So every coloured button, gradient heading and logo was hidden, including the sign in button. This was found from screenshots of every page and fixed by changing all 163 affected classes to the current syntax.

When the sales data were first loaded, every row was assigned to the installation's single restaurant, so the original restaurant numbers were lost. This did not affect the daily totals, but it would have removed one of the most useful features from the item level models. The original number is now stored in its own column.

The first design of the comparison scored an item level model by summing its predictions over each test day. The exploratory analysis in Chapter 3 showed that this uses the number of rows on the day, which is not known in advance. So the design was changed to the two tracks described there.

Windows batch files with Unix line endings fail in ways hard to notice, and paths with spaces break many scripts. Both were found by testing the launchers on a fresh copy of the project and were fixed.

## 5.10 Summary

The implementation follows the design closely. The main engineering decisions were to keep model training apart from serving, to make the application install and start without an internet connection, a database server or the machine learning libraries, and to compute every number shown to the user from stored results or the database. The next chapter explains how it was tested against its requirements.
