# 3 Methodology

## 3.1 Introduction

This chapter describes the methodology used in answering the research questions. It provides information on the research design, how the software was constructed, the data and its quality, the exploratory analysis, the controlled comparison, and the steps taken for the preparation simulation and for making the results reliable.

## 3.2 Research philosophy and design

The project has a positivist approach. Its questions are about measurable things, such as forecast errors, overproduction and the percentage of the demand satisfied. These are answered using quantitative analysis. All the evidence is secondary data. But the comparison is an experimental one, as the training and testing conditions of all models are intentionally controlled.

The work is also based on the logic of design science research. In this type of research, an artefact is created to solve a real world problem and then thoroughly tested against it (Hevner et al., 2004). In this case, the artefact is the EcoServe AI application with its forecasting pipeline. Its evaluation has three parts, each of which connects a research question to a kind of evidence. The forecasting methods are tested by a controlled comparison on days the models have not seen (RQ1 and RQ2). Their effects on food preparation are tested by a simulation with clearly stated assumptions (RQ3). The software is tested against its requirements by means of automated tests (RQ4).

## 3.3 Development approach

The software was created in cycles, in line with the concepts of the Dynamic Systems Development Method (DSDM). In DSDM, scope changes while time and quality are kept constant. It ranks features with the MoSCoW scheme. It puts each requirement into one group, Must have, Should have, Could have or Will not have this time (Agile Business Consortium, 2014). This suited a project that was time constrained and had only one developer working on it. Reliability and honest reporting were the most important qualities of the product and could not be sacrificed.

It was divided into six increments, each with a fixed timebox. Each one finished with a working and tested system. The first one made the application start reliably on a new machine. The second made every figure in the interface traceable back to the data. The third constructed the controlled comparison, the fourth the preparation simulation, the fifth the automated test suite and the sixth this report. Ordering by risk meant that what a demonstration needs most, a system that starts and runs, was secured first. Sommerville (2016) points out that incremental delivery reduces the cost of change, while providing early feedback on the most critical functions. Both benefits were seen.

## 3.4 Data source

Only the Restaurant Sales Report dataset is used as the data source. It was published on Kaggle by Chen (2025) under the Creative Commons Attribution ShareAlike 4.0 licence. The file used is restaurant_sales_data.csv. It is the same size as the published version (1,304,756 bytes) and is used without modification. The file has 10,000 rows. The numbers in each row show the total quantity of a particular menu item sold by a particular restaurant on one day. It also provides the type of restaurant, the type of meal, the typical cost of ingredients, the observed market price and the actual selling price. It has flags for promotions and special events, and the weather. Data are for 50 restaurants of five types and 14 menu items. They cover 367 days, from 1 January 2024 to 1 January 2025.

The publisher does not say how the data were gathered. So it cannot be ascertained if they were taken from real restaurants or created. This restricts how far the results can be applied to other settings (Section 3.12). There is no personal information in the data.

## 3.5 Data quality

Before any modelling, all the data were checked for missing values, duplicates, impossible values and gaps in time. There are no missing values and no exact duplicate rows. However, there are 601 rows that are repeated with the same restaurant, menu item and day, with the same meal type but a different quantity. Without documentation, it is unknown whether these are separate sales sessions or recording mistakes. So they were kept as separate observations, summed on a daily basis and forecast individually at item level.

There are 0 to 1,668 portions per row. The median is 245 and the mean is 286. There are 502 rows with no sales. They were retained, as selling nothing is a real possibility when planning preparation. But zero values make the mean absolute percentage error undefined or extreme (Hyndman and Koehler, 2006). This is one of the reasons why this project opts for the weighted absolute percentage error as the primary measure. The daily series has no gaps, as all 367 calendar days have sales.

## 3.6 Exploratory analysis

The exploratory analysis asked which forecasting tasks the data could support and what a fair comparison would need. Total daily demand across all restaurants (Figure 3.1) averages 7,793 portions with a standard deviation of 2,573 and changes sharply from day to day.

![Figure 3.1 Total portions sold per day, with the test period shaded](figures/fig_daily_demand.png)

Figure 3.2 shows the strength of the recorded drivers. Rows with a promotion sell 482 portions on average, against 251 without one, 92 per cent more. Weekend rows sell 46 per cent more than weekday rows, and special event rows 29 per cent more. Breakfast items sell about twice as much per row as lunch or dinner items. Weather makes little difference. These large effects work at the level of a single restaurant and menu item, which suggests that a model at that level with these inputs should explain much of the variation.

![Figure 3.2 Mean portions sold per row by promotion, weekend, special event and meal type](figures/fig_demand_drivers.png)

The daily total behaves differently. Its correlation with the day before is only 0.06, so yesterday's demand says almost nothing about today's. But its correlation with the same weekday one and two weeks earlier is 0.33, a weekly pattern (Figure 3.3). So a model of the daily total can hope to learn the weekly cycle and average level, but little more from history alone.

![Figure 3.3 Autocorrelation of total daily demand. Dashed lines mark approximate 95 per cent bounds](figures/fig_autocorrelation.png)

The key finding concerns the number of rows recorded per day. It ranges from 13 to 42 with a mean of 27, and has no correlation from one day to the next (minus 0.02). Alone, it explains 38 per cent of the variance in the daily total (Figure 3.4). So much of the movement in total demand comes from how many restaurant and menu item combinations happen to appear on a day. This cannot be known in advance, which has two effects. First, a model of the daily total must not be given the number of rows on the day it forecasts, as that would be future information. Second, a model that adds up its row predictions over the rows that really occurred will look far more accurate at daily level than a real forecast could, because it secretly knows how many rows there are (Section 3.7.5).

![Figure 3.4 Total daily demand against the number of sales rows recorded on the day](figures/fig_records_vs_total.png)

The data also cannot support a separate time series for each restaurant and menu item. There are 274 such combinations, with 2 to 9 items per restaurant. A typical combination appears on only 33 days of the year, at irregular gaps. Time series models that learn from the order of past values, such as LSTM and Prophet, need longer and more regular series.

## 3.7 Controlled model comparison

### 3.7.1 Two comparison tracks

The exploratory findings resulted in a comparison in two tracks. Track A predicts the total demand for each day. This is the problem that LSTM and Prophet are intended to solve, and it addresses RQ1. Track B forecasts the quantity in each row, for one restaurant, one menu item and one day. This is the level at which preparation decisions are made, and it answers RQ2. Within each track, every model receives the same information. As a result, differences in error can be related to the models, not to their inputs.

### 3.7.2 Training and test split

The same split by date is used for both tracks. The first 80 per cent of the days, from 1 January to 19 October 2024 (293 days), are used for training. The last 20 per cent, from 20 October 2024 to 1 January 2025 (74 days), are used only for testing. At item level this results in 7,969 training rows and 2,031 test rows. A split by date is essential, as a random split would allow the models to learn from days after the ones they are tested on (Tashman, 2000).

### 3.7.3 Track A design

In Track A, each model predicts one day ahead using the same history, the demand of each day up to the day before. There are two information sets, and each model is run twice. Information set A1 includes the calendar, indicated by the day of the week and a weekend flag. Information set A2 also adds four covariates for the day being predicted. These are the share of sales rows with a promotion, with a special event, with rainy weather and with cloudy weather. They are assumed to be known beforehand, that is, that a restaurant plans its promotions and events and has an accurate weather forecast. Comparing A1 with A2 shows how much the extra information is worth. Comparing models within one information set shows the effect of the algorithm alone. The number of rows on the day is never used.

Five forecasting methods are compared. Of these, two are baselines which any useful model should surpass. The mean baseline predicts the average demand for all days up to the day before. The seasonal naive baseline predicts the demand on the same weekday one week earlier, a standard benchmark for series with a weekly cycle (Hyndman and Athanasopoulos, 2021). Prophet has been fitted with a weekly seasonality, and in A2 it also uses the four covariates as extra regressors (Taylor and Letham, 2018). It is refitted before each forecast on all demand up to the day before, so it uses the same history as the other models. Yearly seasonality is turned off because the training period is shorter than one year. An earlier setup that tried to estimate it gave very poor forecasts. The LSTM reads the previous 28 days of demand through a recurrent layer of 32 units with dropout of 0.2. It combines this with the calendar and covariates of the target day, and then a small dense layer produces the forecast. It is trained with the Adam optimiser on standardised demand. 20 per cent of the training windows are held back for early stopping. The Random Forest uses 300 trees. It gets the same calendar and covariates, together with demand lagged by 1, 2, 3, 7 and 14 days and the averages of the previous 7 and 28 days. This matches the history the LSTM reads from its window.


### 3.7.4 Robustness checks for Track A

A single split of 74 test days can favour one model by chance. So Track A was repeated with rolling origin evaluation, which tests from several starting points (Tashman, 2000, Bergmeir and Benítez, 2012). The last 40 per cent of the year was split into four consecutive windows of about 37 days, each tested after training on all earlier days, and the mean and standard deviation of the error across windows are reported.

### 3.7.5 Track B design

In Track B there is one prediction for each restaurant, menu item and day recorded in the data. A kitchen would know these as the items on its menu that day. Every model uses the same row features, which are the restaurant, the restaurant type, the menu item, the meal type, the three price and cost variables, the promotion and event flags, the weather, the day of the week, the weekend flag and the month. Two history features are added, the average quantity sold by the same restaurant for the same menu item on all earlier days and the number of such earlier observations. They use only earlier days, so they never contain information from the same day or the future. Such leakage would otherwise be easy to add (Kaufman et al., 2012). When a combination has no earlier observations, the history feature takes the menu item's training average.

Six models are compared. The mean baseline predicts the overall training average. The historical average rule predicts the training average for the menu item. A restaurant could do this with a spreadsheet, and it is the baseline that matters most for RQ2. The four learned models are a regularised linear regression, a neural network with two hidden layers of 64 and 32 units, a Random Forest with 300 trees and a histogram based gradient boosting model (Pedregosa et al., 2011). LSTM and Prophet are left out because, as Section 3.6 showed, the single series are too short and irregular for them.

An earlier version of this system scored an item level Random Forest by summing its predictions over the rows that occurred on each test day and comparing the result with the time series models. For the reason given in Section 3.6, this is unfair, so the figure appears only as a labelled reference showing the size of the hidden information effect, never treated as a forecast or picked as the best model.

### 3.7.6 Error measures

Five measures are reported for every model. The mean absolute error (MAE) and the root mean squared error (RMSE) are in portions, and RMSE weights large errors more. The mean absolute percentage error (MAPE) is reported for completeness, despite its problems with small and zero values. The weighted absolute percentage error (WAPE) divides the total absolute error by the total demand. It equals the ratio recommended by Kolassa and Schütz (2007) and is the main measure in this report. The coefficient of determination (R²) compares a model with always predicting the mean of the test period, so zero means no improvement on the mean and one a perfect forecast.

No figure called accuracy is reported. Taking WAPE away from 100 gives a number that looks like a percentage of correct forecasts, but it has no standard meaning and can be high for a model no better than the average, as happened in an earlier version of this work.

### 3.7.7 Significance testing

To decide if an error difference between two models is bigger than chance would explain, the project uses the test of Diebold and Mariano (1995) for one step ahead forecasts, with the small sample correction of Harvey, Leybourne and Newbold (1997). For each pair, the test compares absolute errors on the same test days and gives a p value. A value below 0.05 is taken as evidence that the two models differ. At item level, the differences in absolute error are first added up for each test day, because rows from the same day are not independent, so the test again uses 74 daily values. Each model is tested against the relevant baseline, the mean baseline in Track A and the historical average rule in Track B, and against the best model of its track. The test was also checked with simulated data (Chapter 6).

## 3.8 Preparation simulation

The dataset has no waste measurements, so the effect of better forecasts on waste was simulated. The simulation replays two preparation plans on the 2,031 item level test rows, one using the historical average rule and the other the best Track B model. For each row and plan, the quantity prepared is the forecast multiplied by one plus a safety margin. Portions prepared but not sold count as overproduction, and demand above the quantity prepared as unmet demand. The share of demand served is the total quantity sold from what was prepared, divided by the total demand. Overproduction is valued at the row's typical ingredient cost, and unmet demand at the selling price minus that cost. This follows the newsvendor problem, which weighs the cost of preparing too much against that of preparing too little (Petruzzi and Dada, 1999).

Every margin from 0 to 20 per cent was simulated, and two comparisons sum up the results. The first compares overproduction and the share of demand served at the application's default margin of 10 per cent. The second finds the margin at which the model plan serves the same share of demand as the historical average plan at 10 per cent, and then compares overproduction. To show how much the results depend on which days fell in the test period, the 74 test days were resampled with replacement 1,000 times, keeping each day's rows together, to give 95 per cent confidence intervals (Efron and Tibshirani, 1993).

The simulation rests on stated assumptions, shown in the application and here. Unsold portions are treated as waste, because prepared food goes off. Recorded sales are treated as true demand, assuming sales were never limited by food running out. Each plan covers the restaurant, menu item and day combinations recorded in the data. It treats promotions, events and weather as known in advance and uses the same margin for every row. The matched service comparison picks its margin on the test days themselves, so it is optimistic. The comparison at a fixed margin involves no such choice. So the figures are estimates of overproduction, not measurements of food waste.

## 3.9 Anomaly detection

The application also flags unusual days in total daily sales. A day's Z score is its distance from the mean in standard deviations. A day is flagged when its Z score is above 3, or it lies outside the fences of Tukey (1977), that is, below the first quartile minus 1.5 times the interquartile range or above the third quartile plus 1.5 times that range. Flagged days more than four standard deviations from the mean are called high severity and the others medium. These rules are standard and clear (Chandola, Banerjee and Kumar, 2009) and were chosen because a manager can see why a day was flagged.

## 3.10 Testing approach

Each requirement in Chapter 4 has an identifier. For every check, the automated test suite records the requirement it supports, the input, and the expected and observed results. Chapter 6 describes the suite and its results.

## 3.11 Reproducibility

All randomness uses a fixed seed, and three full pipeline runs gave the same results. The offline pipeline, precompute.py, writes every result to a single file, results.json, which ships with the application and is loaded on first start, so the interface shows exactly these results. Every report figure was made by a script from the same file.

## 3.12 Validity and reliability

Internal validity is the confidence that the observed differences come from the models, not the design. It is protected because every model in a track gets the same information, history, split and test days. History features use earlier days only, and information not known in advance is left out. Statistical conclusion validity is supported by the significance tests, rolling origin repeats and bootstrap confidence intervals. But a test period of 74 days limits the power to find small differences. So a non significant result should be read as no evidence of a difference, not as proof that the models are equal. Construct validity is weakest for the simulation, because overproduction under stated assumptions is a stand in for waste, not waste itself. External validity is limited because the project uses a single one year dataset of unclear origin. Chapter 7 discusses these limitations further.

## 3.13 Ethical considerations

The project uses only a public dataset with no personal data and involves no human participants. The dataset's licence requires credit to the author, so it is credited in the application, source code and this report. Accounts created in the application exist only on the computer where it is installed and are not used for research. Results are reported without overstating them, which the BCS Code of Conduct treats as a matter of professional integrity (BCS, n.d.).
