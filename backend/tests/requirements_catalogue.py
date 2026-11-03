"""Requirements the test suite traces to. The same IDs are used in the report."""

REQUIREMENTS = {
    # Functional requirements
    "FR-01": ("Functional", "A user can create an account; invalid or duplicate registrations are rejected."),
    "FR-02": ("Functional", "A registered user can sign in with email and password; wrong credentials are rejected."),
    "FR-03": ("Functional", "Application data is only available to signed-in users."),
    "FR-04": ("Functional", "A user can record sales; invalid sales entries are rejected with a message."),
    "FR-05": ("Functional", "A user can view sales history and the latest-day sales overview, and search sales."),
    "FR-06": ("Functional", "A user can log waste entries; invalid entries are rejected with a message."),
    "FR-07": ("Functional", "The waste overview keeps simulated overproduction separate from logged waste."),
    "FR-08": ("Functional", "The system presents a model comparison for daily total and item-level demand, with error "
                            "metrics, rolling-origin results and significance tests."),
    "FR-09": ("Functional", "Models within a comparison track receive the same information and are evaluated on the "
                            "same unseen test days, with no information from the test period used in training."),
    "FR-10": ("Functional", "The system simulates preparation plans and reports overproduction, unmet demand and the "
                            "share of demand served for safety margins from 0% to 20%."),
    "FR-11": ("Functional", "The system provides a preparation plan per menu item for each test day and lets the user "
                            "mark a suggestion as applied."),
    "FR-12": ("Functional", "The system flags unusual sales days using a Z-score above 3 or the 1.5 IQR rule around "
                            "the first and third quartiles."),
    "FR-13": ("Functional", "A user can download sales, waste, forecast, comparison and simulation data as CSV."),
    "FR-14": ("Functional", "The dashboard summarises the latest day, the best model's error and simulated "
                            "overproduction."),
    "FR-15": ("Functional", "Inventory is shown and clearly marked as illustrative demo data."),
    "FR-16": ("Functional", "Retraining can be requested and is refused safely when the machine learning libraries are "
                            "not installed."),
    # Non-functional requirements
    "NFR-01": ("Non-functional", "The application starts with no database server and no machine learning libraries, "
                                 "using SQLite and the shipped pre-computed results."),
    "NFR-02": ("Non-functional", "Main API requests respond within one second on a standard laptop."),
    "NFR-03": ("Non-functional", "Passwords are stored only as bcrypt hashes; sessions use signed tokens that expire "
                                 "after 30 minutes of inactivity."),
    "NFR-04": ("Non-functional", "Invalid input and unknown endpoints return clear 4xx responses instead of server "
                                 "errors."),
    "NFR-05": ("Non-functional", "All data comes from one public, attributed dataset that contains no personal data."),
    "NFR-06": ("Non-functional", "Metrics, statistical tests and the simulation are computed correctly and "
                                 "reproducibly."),
    "NFR-07": ("Non-functional", "Results are reported honestly: no 'accuracy' figure, and simulated values are "
                                 "labelled as simulated."),
}
