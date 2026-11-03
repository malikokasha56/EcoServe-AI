# 6 Testing

## 6.1 Introduction

There were two goals for testing. The first was to show, with evidence that anybody can easily check, that the application fulfils all the requirements from Chapter 4. The second was to show that the calculations that lead to the results are correct. If a calculation is wrong, the conclusions are wrong regardless of how well the software performs.

## 6.2 Strategy

Testing was set up in four levels. Unit tests test the machine learning code by applying it to small examples with answers worked out by hand. If there is any mistake in the code, it shows as a difference between the expected result and the observed result. Integration tests send real requests to the application programming interface and check the responses. They use a temporary database that is built exactly as on the first start up of a new installation. Data tests check where the data came from and that the stored results agree with each other. System tests check the entire application on a fresh copy of the project, including the installation, start up and each page of the interface in a browser.

The first three levels are automated using pytest and take about thirty seconds to run. Each test is linked to one or more requirement identifiers. Every check performed inside a test is documented with its input, expected result and observed result. Once the suite is completed, it writes the complete evidence table and a requirements traceability matrix to the docs/testing folder of the project. So the evidence presented in this chapter and Appendix B was made by the tests themselves, not copied. A failed test records the observed result that caused the failure.

## 6.3 Results of the automated suite

There are 90 tests in the suite. Of these, 67 test the programming interface, 17 the machine learning code and 6 the data and the stored results. All 90 passed (Figure 6.1). Each of the 23 requirements is covered by at least one test. The coverage is summarised in Table 6.1, and the full traceability matrix is given in Appendix A.

![Figure 6.1 Output of the automated test suite](figures/term_tests.png)

Table 6.1 Test coverage by requirement

| Requirement | Tests | Result | Requirement | Tests | Result |
|---|---|---|---|---|---|
| FR-01 Accounts | 5 | Pass | FR-13 CSV export | 5 | Pass |
| FR-02 Sign in | 2 | Pass | FR-14 Dashboard | 1 | Pass |
| FR-03 Access control | 7 | Pass | FR-15 Inventory labelled | 1 | Pass |
| FR-04 Record sales | 8 | Pass | FR-16 Retraining safeguards | 2 | Pass |
| FR-05 Sales history | 2 | Pass | NFR-01 Starts without servers or ML libraries | 2 | Pass |
| FR-06 Log waste | 7 | Pass | NFR-02 Response time | 7 | Pass |
| FR-07 Waste sources separate | 1 | Pass | NFR-03 Security | 4 | Pass |
| FR-08 Model comparison | 6 | Pass | NFR-04 Invalid input handled | 21 | Pass |
| FR-09 Equal information, no leakage | 11 | Pass | NFR-05 Public data only | 4 | Pass |
| FR-10 Preparation simulation | 7 | Pass | NFR-06 Correct and reproducible | 8 | Pass |
| FR-11 Preparation plan | 3 | Pass | NFR-07 Honest reporting | 5 | Pass |
| FR-12 Anomaly detection | 2 | Pass | | | |

Table 6.2 shows some recorded checks, picked to show the different kinds of test. Appendix B contains all 90.

Table 6.2 Selected test evidence

| Test | Requirement | Input | Expected result | Observed result |
|---|---|---|---|---|
| T-01 | NFR-01 | Health check on a new database | Ready, SQLite, 10,000 sales records, results loaded | Ready, SQLite, 10,000 records, 15 results |
| T-09 | FR-02 | Sign in with a wrong password | 401 with a message | 401, Invalid email or password |
| T-27 | FR-04, NFR-04 | Record a sale with an empty item name | 400 with a message | 400, Each item needs a name |
| T-38 | FR-07, NFR-07 | Waste overview after logging one entry | Separate simulated and logged sections | 98,733 simulated portions labelled as simulated, 1 logged entry |
| T-43 | FR-10 | Recompute the headline reduction from the simulation grid | 34.1 per cent | 34.1 per cent, interval 25.4 to 40.8 |
| T-61 | NFR-02 | Request the model comparison | Response under 1,000 ms | 38 ms |
| T-68 | NFR-05 | Size of the dataset file | 1,304,756 bytes, as published | 1,304,756 bytes |
| T-74 | NFR-06 | Actual 100, 200, 300 and forecast 110, 190, 330 | MAE 16.667, RMSE 19.149, WAPE 8.333, R² 0.945 | Identical values |
| T-77 | NFR-06 | 200 trials of two equally good forecasts | About 5 per cent called different | 4.0 per cent |
| T-80 | FR-09 | Sales of 10 on day 1, 20 and 40 on day 2, 30 on day 3 | Day 2 sees only 10, day 3 sees 10, 20 and 40 | Averages 10.0 and 23.33 from 1 and 3 earlier sales |
| T-86 | FR-10 | Demand 10 and 20, forecast 10 and 10, margin 10 per cent | Prepared 22, overproduction 1, unmet 9, served 70 per cent | Identical values |
| T-90 | FR-12 | Values from 90 to 110 and one value of 500 | Only 500 flagged, fences at Q1 and Q3 plus or minus 1.5 IQR | Only 500 flagged, fences 79.5 and 121.5 |

## 6.4 Tests of the calculations

The unit tests require special attention, as they protect the correctness of the results rather than the behaviour of the software. The error measures are compared with a calculation made by hand on three values (T-74). Zero demand is checked separately. This verifies that the percentage error skips days where there is no demand, and that the weighted percentage error is undefined when all demand is zero. The significance test is checked in two ways. If one forecast is clearly better, the test gives a very small p value, the same in either order (T-76). If two forecasts are equally good, it calls them different in 4.0 per cent of 200 simulated trials (T-77). This is close to the 5 per cent which would be expected by chance, so the test does not set off false alarms more often than it should.

The tests of the comparison design check that there is no count of rows on the day being forecast in the inputs of the daily models. They verify that a missing day becomes a day of zero demand, rather than being removed from the series. They also ensure that the seasonal naive baseline repeats the value from seven days earlier, and that all training rows of the item level track come before all test rows. The history feature is checked on a small example of an item sold on four different days, two of them on the same date. The observed averages show that each day sees only earlier days (T-80). Further tests confirm that the mean baseline uses all demand up to the day before, that the item level significance test is based on daily totals, and that the pipeline reads only the rows of the public dataset, not sales entered in the application. The simulation is compared with a hand calculation (T-86). It is checked against the rule that a larger margin can never reduce either the overproduction or the share of demand served. It is checked against the definition of the matched margin (T-89), and its confidence intervals must be identical when it is run twice.

To check that these tests would detect real faults, two faults were put into the code on purpose and the suite was run again. In the first, an additional portion was added to the overproduction of each row. In the second, the sales of the current day itself were added to the history feature. This is exactly the leakage that the design is supposed to prevent. In both cases the matching test failed with a clear message, and all the tests passed again when the original code was put back. This mutation check provides some assurance that the passing tests are meaningful and not vacuously true.

## 6.5 System tests

The automated suite tests the application through its programming interface, but the experience of a user also depends on the launcher, the installation and the pages in the browser. These were tested on a fresh copy of the project in a folder whose name contains spaces, with no environment, no database and no compiled packages. Table 6.3 summarises the results.

Table 6.3 System tests on a fresh installation

| Test | Expected result | Observed result |
|---|---|---|
| First start with START.bat and no internet connection needed | Environment created from bundled packages, five checks reported, browser opens | As expected, installation from the bundled packages in about a minute |
| Second start | Existing environment reused, start in seconds | As expected |
| Port 5000 already in use | Next free port chosen and shown | Port 5051 chosen when 5050 was occupied |
| Self contained EcoServe.exe copied to a separate folder and started on its own | Application starts and passes the interface tests | All interface checks passed |
| Every page opened in a browser after sign in | Data shown, no loading or error states, no script errors | All 15 pages passed with no console errors |
| Interactive controls | Comparison tabs, information set toggle, margin slider and day selector update the page | All updated correctly |
| RUN_TESTS.bat on a laptop without the machine learning libraries | Interface and data tests run, machine learning tests reported as skipped | 73 passed, machine learning module reported as skipped |

## 6.6 Limitations of the testing

The testing has three limits that should be stated. No usability testing with real users was done, because the project had no human participants. So the clarity of the interface was judged against the design principles in Chapter 4, not measured. The frontend code has no automated unit tests of its own. Its behaviour was checked instead by opening every page in an automated browser and looking at screenshots. The response times were measured on one laptop and through the test client. So they show that the server is fast, but they do not describe performance with many users at the same time. That is outside the scope of a single site prototype.

## 6.7 Summary

The automated suite of 90 tests passed in full and covers all 23 requirements. Evidence was recorded for each check as input, expected result and observed result. The calculations behind the results were checked against hand calculations, and the tests were shown to find faults added on purpose. System tests confirmed that the application installs and starts on a fresh copy without an internet connection, a database server or the machine learning libraries.
