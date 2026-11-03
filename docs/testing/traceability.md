# Requirements Traceability

Generated automatically by the test suite on 2026-10-19 15:34. Each requirement lists the tests that provide evidence for it.

| Requirement | Type | Description | Tests | Status |
|---|---|---|---|---|
| FR-01 | Functional | A user can create an account; invalid or duplicate registrations are rejected. | T-03, T-04, T-05, T-06, T-07 | Pass (5/5) |
| FR-02 | Functional | A registered user can sign in with email and password; wrong credentials are rejected. | T-08, T-09 | Pass (2/2) |
| FR-03 | Functional | Application data is only available to signed-in users. | T-10, T-11, T-12, T-13, T-14, T-15, T-16 | Pass (7/7) |
| FR-04 | Functional | A user can record sales; invalid sales entries are rejected with a message. | T-21, T-22, T-23, T-24, T-25, T-26, T-27, T-28 | Pass (8/8) |
| FR-05 | Functional | A user can view sales history and the latest-day sales overview, and search sales. | T-29, T-30 | Pass (2/2) |
| FR-06 | Functional | A user can log waste entries; invalid entries are rejected with a message. | T-31, T-32, T-33, T-34, T-35, T-36, T-37 | Pass (7/7) |
| FR-07 | Functional | The waste overview keeps simulated overproduction separate from logged waste. | T-38 | Pass (1/1) |
| FR-08 | Functional | The system presents a model comparison for daily total and item-level demand, with error metrics, rolling-origin results and significance tests. | T-39, T-41, T-71, T-72, T-76, T-77 | Pass (6/6) |
| FR-09 | Functional | Models within a comparison track receive the same information and are evaluated on the same unseen test days, with no information from the test period used in training. | T-40, T-41, T-71, T-78, T-79, T-80, T-81, T-82, T-83, T-84, T-85 | Pass (11/11) |
| FR-10 | Functional | The system simulates preparation plans and reports overproduction, unmet demand and the share of demand served for safety margins from 0% to 20%. | T-42, T-43, T-73, T-86, T-87, T-88, T-89 | Pass (7/7) |
| FR-11 | Functional | The system provides a preparation plan per menu item for each test day and lets the user mark a suggestion as applied. | T-44, T-45, T-46 | Pass (3/3) |
| FR-12 | Functional | The system flags unusual sales days using a Z-score above 3 or the 1.5 IQR rule around the first and third quartiles. | T-47, T-90 | Pass (2/2) |
| FR-13 | Functional | A user can download sales, waste, forecast, comparison and simulation data as CSV. | T-48, T-49, T-50, T-51, T-52 | Pass (5/5) |
| FR-14 | Functional | The dashboard summarises the latest day, the best model's error and simulated overproduction. | T-53 | Pass (1/1) |
| FR-15 | Functional | Inventory is shown and clearly marked as illustrative demo data. | T-54 | Pass (1/1) |
| FR-16 | Functional | Retraining can be requested and is refused safely when the machine learning libraries are not installed. | T-55, T-56 | Pass (2/2) |
| NFR-01 | Non-functional | The application starts with no database server and no machine learning libraries, using SQLite and the shipped pre-computed results. | T-01, T-02 | Pass (2/2) |
| NFR-02 | Non-functional | Main API requests respond within one second on a standard laptop. | T-60, T-61, T-62, T-63, T-64, T-65, T-66 | Pass (7/7) |
| NFR-03 | Non-functional | Passwords are stored only as bcrypt hashes; sessions use signed tokens that expire after 30 minutes of inactivity. | T-17, T-18, T-19, T-20 | Pass (4/4) |
| NFR-04 | Non-functional | Invalid input and unknown endpoints return clear 4xx responses instead of server errors. | T-04, T-05, T-06, T-07, T-22, T-23, T-24, T-25, T-26, T-27, T-28, T-32, T-33, T-34, T-35, T-36, T-37, T-45, T-57, T-58, T-59 | Pass (21/21) |
| NFR-05 | Non-functional | All data comes from one public, attributed dataset that contains no personal data. | T-68, T-69, T-70, T-84 | Pass (4/4) |
| NFR-06 | Non-functional | Metrics, statistical tests and the simulation are computed correctly and reproducibly. | T-74, T-75, T-76, T-77, T-83, T-86, T-87, T-88 | Pass (8/8) |
| NFR-07 | Non-functional | Results are reported honestly: no 'accuracy' figure, and simulated values are labelled as simulated. | T-38, T-54, T-67, T-72, T-73 | Pass (5/5) |

Requirements covered: 23 of 23.
