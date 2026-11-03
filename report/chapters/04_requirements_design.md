# 4 Requirements and Design

## 4.1 Introduction

This chapter sets out what the EcoServe AI application must do and how it was designed. Its requirement IDs match those used by the automated tests in Chapter 6, so every requirement links to evidence that it has been met.

## 4.2 Sources of requirements

No people were consulted, so the requirements were derived by analysis from three sources. The first is the literature in Chapter 2, which shows that a useful forecasting based decision support system needs forecasts at the level of the decision, open evaluation and a clear link between forecasts and actions (Arnott and Pervan, 2014). The second is the dataset, which decides what can be forecast, at what level and with which inputs, and what cannot be offered, such as measured waste or real stock levels. The third is the need to show and assess the system, which makes reliability, repeatable results and honest presentation into real requirements, not just nice qualities.

## 4.3 Users and use cases

Two roles were found. The restaurant manager uses the application to understand demand, plan preparation, record sales and waste, and look at the evidence behind the forecasts. The analyst, who may be the same person, retrains the models when new data arrive and checks the comparison results. Table 4.1 lists the resulting use cases.

Table 4.1 Use cases

| ID | Use case | Actor | Description |
|---|---|---|---|
| UC1 | Create an account and sign in | Manager | Register with an email and password, then sign in to reach the application |
| UC2 | Review the dashboard | Manager | See the latest day's sales and forecast, the best model's error and simulated overproduction |
| UC3 | Record sales | Manager | Enter the items and quantities sold on a day |
| UC4 | Log waste | Manager | Record an item that was thrown away, its quantity, unit, reason and cost |
| UC5 | Compare forecasting models | Manager, Analyst | Read the results of both comparison tracks, the significance tests and the method |
| UC6 | Explore the preparation simulation | Manager | Compare the two preparation plans at any safety margin from 0 to 20 per cent |
| UC7 | Use the preparation plan | Manager | See suggested quantities per menu item for a day and mark them as applied |
| UC8 | Investigate unusual days | Manager | See which days had unusually high or low total sales and why they were flagged |
| UC9 | Export data | Manager, Analyst | Download sales, waste, forecasts, comparison and simulation results as CSV files |
| UC10 | Retrain the models | Analyst | Rerun the offline pipeline when the machine learning libraries are installed |

## 4.4 Functional requirements

Table 4.2 lists the functional requirements, each with a MoSCoW priority (Agile Business Consortium, 2014). Without the requirements marked Must, the system would not answer the research questions or could not be used at all.

Table 4.2 Functional requirements

| ID | Requirement | Priority | Use case |
|---|---|---|---|
| FR-01 | A user can create an account, and invalid or duplicate registrations are rejected | Must | UC1 |
| FR-02 | A registered user can sign in with email and password, and wrong credentials are rejected | Must | UC1 |
| FR-03 | Application data are available only to signed in users | Must | UC1 |
| FR-04 | A user can record sales, and invalid sales entries are rejected with a message | Should | UC3 |
| FR-05 | A user can view sales history and the latest day's overview, and search sales | Should | UC3 |
| FR-06 | A user can log waste entries, and invalid entries are rejected with a message | Should | UC4 |
| FR-07 | The waste overview keeps simulated overproduction separate from logged waste | Must | UC4 |
| FR-08 | The system presents the model comparison for daily and item level demand with error measures, rolling origin results and significance tests | Must | UC5 |
| FR-09 | Models within a track receive the same information and are tested on the same unseen days, with no test period information used in training | Must | UC5 |
| FR-10 | The system simulates preparation plans and reports overproduction, unmet demand and the share of demand served for margins from 0 to 20 per cent | Must | UC6 |
| FR-11 | The system provides a preparation plan per menu item for each test day and lets the user mark a suggestion as applied | Should | UC7 |
| FR-12 | The system flags unusual sales days using a Z score above 3 or the interquartile range fences around the quartiles | Could | UC8 |
| FR-13 | A user can download sales, waste, forecast, comparison and simulation data as CSV | Should | UC9 |
| FR-14 | The dashboard summarises the latest day, the best model's error and simulated overproduction | Should | UC2 |
| FR-15 | Inventory is shown and clearly marked as illustrative demo data | Could | UC2 |
| FR-16 | Retraining can be requested and is refused safely when the machine learning libraries are not installed | Could | UC10 |

## 4.5 Non functional requirements

The non functional requirements in Table 4.3 describe qualities, not functions. Some are unusual for a prototype, such as starting without a database server or machine learning libraries, and reporting results honestly. But a system that cannot be shown working, or that overstates its results, fails its purpose however good its models are.

Table 4.3 Non functional requirements

| ID | Requirement | Priority | How it is verified |
|---|---|---|---|
| NFR-01 | The application starts with no database server and no machine learning libraries, using SQLite and the shipped results | Must | Fresh installation test and import scan |
| NFR-02 | Main requests respond within one second on a standard laptop | Should | Timed requests |
| NFR-03 | Passwords are stored only as bcrypt hashes, and sessions use signed tokens that expire after 30 minutes of inactivity | Must | Inspection of stored data and token tests |
| NFR-04 | Invalid input and unknown endpoints return clear error responses rather than server errors | Must | Requests with invalid input |
| NFR-05 | All data come from one public, attributed dataset with no personal data | Must | File size, header and attribution checks |
| NFR-06 | Measures, statistical tests and the simulation are computed correctly and reproducibly | Must | Hand calculated examples and repeated runs |
| NFR-07 | Results are reported honestly, with no accuracy figure and with simulated values labelled as simulated | Must | Scan of all responses |

## 4.6 Out of scope

Some functions were deliberately placed in the group Will not have this time, so effort could go to the most important requirements. The application does not reset passwords by email, because it runs locally without an email service, and the page for this says so instead of pretending to send a message. It does not connect to a point of sale system, serves one restaurant site, not many, and does not retrain models inside the web server process, because training takes about twenty minutes and would block the application. Inventory is not modelled from real data, because the dataset has no stock records, and its page says so.

## 4.7 Architecture

The architecture in Figure 4.1 splits the system into an online part, which serves the application, and an offline part, which trains the models.

![Figure 4.1 System architecture](figures/fig_architecture.png)

The online part is a normal three layer web application. The presentation layer is a single page application in React and TypeScript that runs in the browser and draws charts with Recharts. The application layer is a Flask server offering a REST interface, checks users with JSON Web Tokens and serves the built frontend. So the whole system runs as one process on one port. The data layer is a relational database used through SQLAlchemy. By default it is SQLite, a single file that needs no installation. PostgreSQL can replace it by changing one configuration value.

The offline part is the forecasting pipeline, which runs the comparison and the simulation and writes every result to a single file shipped with the application. This split was the project's key design decision. Training an LSTM and fitting Prophet need large libraries that are slow to install and can fail on some machines. Keeping them out of the online part means the application starts in seconds on a normal laptop with only Python installed. It answers at once because it serves stored results, and always shows exactly the results reported here.

A launcher script checks the database, the sales data, the demo account, the model results and the built interface, reports each check on screen, picks a free port and opens the browser. For computers without Python, the application is also packaged as a self contained executable.

## 4.8 Data model

The data model in Figure 4.2 has two groups of tables. The operational tables hold the restaurants, the users, the sales records and the waste records. Each sales record keeps the restaurant identifier in this installation and the one in the original dataset, which the item level models need. Waste records have a source field that tells apart entries logged by a user and overproduction estimated by the simulation, so the two can never be added together by mistake.

![Figure 4.2 Data model. Orange tables hold operational data and purple tables hold stored results of the offline pipeline](figures/fig_data_model.png)

The result tables hold the offline pipeline's outputs. The experiment results table has one row per model and track, with every error measure, the rolling origin mean and standard deviation, and the p values of the significance tests. The forecast records table holds each model's forecast and the actual value for every test day. The simulation tables hold results for each plan and margin with a summary of the main comparisons. The recommendations table holds the preparation plan for each test day and menu item alongside the historical average rule and the actual sales.

## 4.9 Programming interface

The frontend talks to the server only through the REST interface summarised in Table 4.4. All endpoints need a valid token, except sign in, registration, the health check and the public summary used by the landing page. Errors are always returned as JSON with a readable message, and unknown paths return a 404 response instead of a server error.

Table 4.4 Main API endpoints

| Area | Endpoints | Purpose |
|---|---|---|
| Authentication | POST /api/auth/register, POST /api/auth/login, GET /api/auth/me | Accounts and sessions |
| Sales | GET and POST /api/sales, GET /api/sales/history, /overview, /menu-items | Record and view sales |
| Waste | GET and POST /api/waste, GET /api/waste/overview, /food-items | Log waste and view simulated overproduction |
| Forecasting | GET /api/forecast, GET /api/forecast/compare, POST /api/forecast/train | Comparison results and retraining |
| Simulation | GET /api/simulation | Simulation grid, headline comparisons and assumptions |
| Preparation | GET /api/recommendations?date=, POST /api/recommendations/id/apply | Daily plans and their status |
| Other | GET /api/dashboard/summary, /api/anomalies, /api/inventory, /api/reports | Dashboard, anomalies, inventory and CSV reports |
| System | GET /api/health, GET /api/public/overview | Readiness checks and public summary |

## 4.10 Interface design principles

The interface follows three principles taken from the requirements. The first is that every number can be traced to the stored results or the database. Summary statements such as the key findings are made from the data, so they stay correct after retraining. The second is that estimates are labelled as estimates, so simulated overproduction is always called simulated, and the inventory page says its data are illustrative. The third is that each measure is explained where it appears, so a manager who reads a WAPE of 21 per cent is told it is the total error as a share of demand and that lower is better. This follows the point that a decision support system is trusted only if users understand what it tells them (Arnott and Pervan, 2014).

## 4.11 Summary

The requirements reflect what the dataset can support and what a decision support tool for preparation planning needs. Sixteen functional and seven non functional requirements were written and prioritised. The architecture separates the slow and fragile model training from the fast and reliable serving of results, which makes the application quick to start and consistent with the reported findings. The next chapter describes how this design was built.
