# 7 Results and Evaluation

## 7.1 Introduction

This chapter gives the results of the controlled comparison, the reference result, the preparation simulation and the anomaly detection, checks the application against its requirements and answers each research question. It ends by critically discussing what the results mean and how far we can trust them. All figures come from the offline pipeline's saved results, which the application also shows.

## 7.2 Daily total demand (Track A)

Table 7.1 gives every model's results on the 74 test days, with rolling origin results and Diebold and Mariano p values against the mean baseline and the model with the lowest error.

Table 7.1 Track A results on the test period

| Model | Information | MAE | RMSE | WAPE (%) | R² | Rolling WAPE (%) | p vs mean | p vs best |
|---|---|---|---|---|---|---|---|---|
| Mean baseline | history | 2,134 | 2,738 | 26.3 | −0.02 | 25.3 ± 4.2 | | 0.002 |
| Seasonal naive | history | 2,175 | 2,908 | 26.8 | −0.15 | 28.3 ± 2.8 | 0.854 | 0.011 |
| Prophet | A1 | 1,695 | 2,294 | 20.9 | 0.28 | 21.1 ± 2.6 | 0.003 | 0.770 |
| LSTM | A1 | 1,789 | 2,391 | 22.1 | 0.22 | 21.0 ± 3.0 | 0.035 | 0.135 |
| Random Forest | A1 | 1,848 | 2,413 | 22.8 | 0.21 | 22.2 ± 2.3 | 0.086 | 0.040 |
| Prophet | A2 | 1,679 | 2,284 | 20.7 | 0.29 | 20.8 ± 2.8 | 0.002 | lowest |
| LSTM | A2 | 1,725 | 2,303 | 21.3 | 0.28 | 21.1 ± 3.0 | 0.004 | 0.495 |
| Random Forest | A2 | 1,740 | 2,396 | 21.5 | 0.22 | 20.9 ± 2.3 | 0.012 | 0.367 |

MAE and RMSE are in portions per day. Every model forecasts one day ahead from demand up to the day before. A1 adds the calendar, and A2 also adds the day's promotion, event and weather mix.

Always predicting the historical average gave a WAPE of 26.3 per cent and an R² of minus 0.02. The seasonal naive forecast was not better (26.8 per cent, p = 0.854) despite the weekly pattern, because one value from the week before carries the pattern but also all that day's noise.

All three forecasting models beat the baselines, with test WAPE from 20.7 to 22.8 per cent and R² from 0.21 to 0.29, so they explained a fifth to nearly three tenths of the day to day change in total demand. With A2, all three were significantly better than the mean baseline (p between 0.002 and 0.012). With A1, Prophet and LSTM were, but the Random Forest was not (p = 0.086).

The more important result concerns how the models differ. Prophet with A2 had the lowest test error, but with the same information neither the LSTM (p = 0.495) nor the Random Forest (p = 0.367) differed significantly from it. Only the Random Forest with the calendar alone (A1) was significantly worse (p = 0.040). The rolling origin results agree. The five best setups have mean errors between 20.8 and 21.1 per cent over the four windows, with standard deviations of 2.3 to 3.0 points, much larger than the gaps between them (Figure 7.1).

![Figure 7.1 Track A error. Bars show the rolling origin mean with one standard deviation, dots show the main split](figures/fig_trackA_wape.png)

Adding the promotion, event and weather mix (A2) helped a little. The LSTM error fell from 22.1 to 21.3 per cent, the Random Forest's from 22.8 to 21.5 per cent and Prophet's from 20.9 to 20.7 per cent. This fits the weak link between these daily shares and the total. Figure 7.2 shows that all three models follow the weekly rhythm and level of demand but miss most of the large peaks and drops.

![Figure 7.2 Forecasts of total daily demand against actual demand in the test period](figures/fig_trackA_series.png)

The reason for this limit lies in the data. Section 3.6 showed that the number of sales rows on the day, which is random and cannot be known in advance, explains 38 per cent of the variance in the daily total. No honest forecast can predict that part of the change, and all three models seem to reach about the same limit.

The models differ in cost. The Random Forest trained in a few seconds, while the LSTM and the daily refitted Prophet took 20 seconds to two minutes for the test period, and the LSTM needed the largest and most fragile software dependency. When models work equally well, this is a fair reason to prefer the simpler ones.

**Answer to RQ1.** Given the same information, LSTM, Prophet and Random Forest forecast total daily restaurant demand with similar error, around 21 to 23 per cent WAPE. All three are significantly better than simple baselines in most setups, but no model is significantly better than the others, and the extra context information makes only a small difference at this level. On this dataset, the choice of algorithm for daily total demand matters less than the information available and how predictable the series itself is.

## 7.3 The reference result

The reference result is an item level Random Forest whose predictions were summed over the rows that really happened on each test day. It reached a WAPE of 7.6 per cent and an R² of 0.79 at daily level. Taken at face value, it would forecast total demand almost three times as accurately as any model in Table 7.1. It does not. Its error is small because the sum uses exactly the rows that existed each day, whose number explains much of the change the real forecasts cannot see. So comparing it with the time series models compares information, not algorithms, which is why this project uses two separate tracks.

## 7.4 Item level demand (Track B)

Table 7.2 gives the six models' results on the 2,031 item level test rows.

Table 7.2 Track B results on the test period

| Model | MAE | RMSE | MAPE (%) | WAPE (%) | R² | p vs rule | p vs best |
|---|---|---|---|---|---|---|---|
| Mean baseline | 169 | 223 | 184.9 | 57.1 | 0.00 | <0.001 | <0.001 |
| Historical average rule | 118 | 160 | 96.7 | 40.1 | 0.48 | | <0.001 |
| Linear regression | 92 | 122 | 67.4 | 31.0 | 0.70 | <0.001 | <0.001 |
| Neural network | 76 | 103 | 67.6 | 25.8 | 0.78 | <0.001 | 0.005 |
| Random Forest | 75 | 103 | 61.5 | 25.5 | 0.79 | <0.001 | 0.025 |
| Gradient boosting | 74 | 101 | 60.3 | 24.9 | 0.79 | <0.001 | lowest |

MAE and RMSE are in portions per restaurant, menu item and day. The p values compare daily totals of absolute errors over the 74 test days.

The picture here is very different from Track A. The historical average rule, which predicts each item's average quantity, already explains about half of the variation (R² 0.48) and cuts the error of the overall mean from 57.1 to 40.1 per cent WAPE. Every learned model beats that rule by far, with very strong statistical support (p < 0.001 in every case). The linear regression reaches 31.0 per cent, and the three nonlinear models between 24.9 and 25.8 per cent with an R² of about 0.79, explaining almost four fifths of the variation in item level demand. Gradient boosting has the lowest error. Its lead over the Random Forest is only 0.6 percentage points but statistically significant (p = 0.025) because it is steady across test days. The models' history feature, used alone as a forecast, scores 40.8 per cent, about the same as the rule. So the gain comes from combining the inputs, not that feature. Figure 7.3 shows the results.

![Figure 7.3 Track B error on 2,031 item level test rows](figures/fig_trackB_wape.png)

MAPE is very high for every model, between 60 and 185 per cent, because many rows have small or zero sales, where a small error is a very large percentage error. WAPE weights errors by demand and is a much better guide.

To see what the best model depends on, we measured how much its test error grows when each input is randomly shuffled (Figure 7.4). The selling price is by far the most important input. Next come the promotion flag, the restaurant's own sales history for the item, the weekend flag, the meal type and the menu item. The weather, special event flag, restaurant identifier and calendar month add almost nothing once the other inputs are known. These are the drivers the exploratory analysis found, suggesting the model has learned the data's structure, not noise.

![Figure 7.4 Importance of each input to the gradient boosting model, measured as the increase in MAE when the input is shuffled](figures/fig_importance.png)

**Answer to RQ2.** Yes. A feature based model forecasting demand for each restaurant, menu item and day is much better than the historical average rule. Gradient boosting cuts the error from 40.1 to 24.9 per cent WAPE and raises R² from 0.48 to 0.79, and every learned model is significantly better than the rule. The gain comes from using price, promotion, the restaurant's own history and the calendar, which the rule ignores.

## 7.5 Preparation simulation

Table 7.3 shows the two preparation plans over the test period at five safety margins, and Figures 7.5 and 7.6 the full range from 0 to 20 per cent.

Table 7.3 Simulated outcomes of the two preparation plans over the test period

| Plan | Margin (%) | Overproduction | Unmet demand | Demand served (%) | Ingredient cost wasted ($) | Margin lost ($) |
|---|---|---|---|---|---|---|
| Historical average rule | 0 | 114,683 | 125,621 | 79.0 | 354,252 | 1,183,365 |
| Historical average rule | 10 | 149,747 | 101,820 | 83.0 | 444,246 | 972,803 |
| Historical average rule | 20 | 188,527 | 81,734 | 86.4 | 543,175 | 790,259 |
| Gradient boosting | 0 | 65,996 | 83,598 | 86.1 | 214,542 | 1,042,759 |
| Gradient boosting | 10 | 98,733 | 58,135 | 90.3 | 296,761 | 801,749 |
| Gradient boosting | 20 | 139,407 | 40,609 | 93.2 | 398,995 | 619,932 |

Quantities are in portions, summed over 2,031 test rows that cover 599,597 portions of demand.

At the default margin of 10 per cent, the gradient boosting plan makes 34.1 per cent fewer extra portions than the historical average plan (98,733 against 149,747). The 95 per cent confidence interval is from 25.4 to 40.8 per cent. It also serves 7.3 percentage points more of the demand (90.3 against 83.0 per cent, interval 5.1 to 9.3 points). So the model plan is better on both measures at once. The simulated cost of wasted ingredients falls from 444,246 to 296,761 dollars over the test period across all 50 restaurants.

![Figure 7.5 Simulated overproduction of each plan at every safety margin](figures/fig_sim_margin.png)

The second comparison fixes the service level, not the margin. It serves the same 83.0 per cent of demand as the historical average plan when its margin is minus 5.5 per cent, so it prepares a little less than its own forecast. There its overproduction is 65.4 per cent lower (interval 61.3 to 68.8 per cent). This figure is optimistic, because the matching margin was chosen on the test days themselves. So the comparison at a fixed margin is the more reliable main result. Figure 7.6 shows the full trade off. At every level of service the model plan makes less extra food, its curve lying fully below and to the right of the rule's.

![Figure 7.6 Trade off between the share of demand served and overproduction. Each point is one margin](figures/fig_sim_tradeoff.png)

Two details limit this picture. At a 10 per cent margin, the share of rows where the model plan falls short is a little higher than for the rule (40.7 against 39.3 per cent), but its shortfalls are much smaller in total. Day by day, the model plan total was closer to actual sales on 56 of the 74 test days. Its total absolute error across items and days was 114,640 portions against 182,952 for the rule, 37 per cent lower. On the other 18 days the rule was closer, so one day is a poor way to judge either plan.

The money figures raise one more point. Here the margin lost on an unserved portion exceeds the ingredient cost of a wasted one, so the total cost of waste and lost sales keeps falling as the margin rises. A restaurant wanting only the lowest cost would accept more waste, while one that also values cutting waste would choose a smaller margin. The simulation does not settle this trade off, but at every margin from 0 to 20 per cent, the model plan has both less waste and less lost margin than the rule.

**Answer to RQ3.** Under the stated assumptions, a preparation plan based on the gradient boosting forecasts would have avoided about a third of the overproduction of a historical average plan (34.1 per cent, interval 25.4 to 40.8 per cent, at a 10 per cent margin) while serving more of the demand. At an equal level of service it would have avoided an optimistic two thirds (65.4 per cent, interval 61.3 to 68.8 per cent). These are simulated estimates of overproduction on historical data, not measurements of food waste in a restaurant.

## 7.6 Anomaly detection

Five of the 367 days were flagged, all for very high total sales (Figure 7.7). They were 25 February, 16 March, 14 April, 15 December and 25 December 2024, with totals between 14,811 and 17,081 portions, against a mean of 7,793 and an upper fence of 14,443. Both rules flagged four, and only the interquartile rule flagged 16 March. None was more than four standard deviations from the mean, so all are medium severity. No low day was flagged, because the lower fence (829 portions) is far below the lowest total. The flags make sense, and include Christmas Day. In a live system they would prompt a manager to look for a reason before using the day's data for planning.

![Figure 7.7 Total daily sales with the five flagged days in red and the upper interquartile fence dashed](figures/fig_anomalies.png)

## 7.7 Evaluation of the application

Chapter 6 showed that all 90 automated tests passed and that recorded evidence covers all 23 requirements. The application installs from bundled packages and starts on a fresh copy with five reported checks. It runs as a self contained executable, every page opened without errors, and the main endpoints answered in 4 to 38 milliseconds. No response contains an accuracy figure, and simulated and example values are marked as such.

**Answer to RQ4.** The methods can be delivered as a decision support application. It starts reliably on a normal laptop, meets all stated requirements and reports its results without overstating them. The main limit is that the application's evaluation was technical, not human, because no users took part.

## 7.8 Critical discussion

### 7.8.1 What the results mean

The two tracks lead to a conclusion more useful than a ranking of algorithms. For total daily demand the algorithm hardly mattered, because the series has little predictable structure beyond its weekly cycle and level. At the preparation level, the available information mattered a lot. This fits the view that no method is best in general and that a model's value depends on the data and the level of aggregation (Makridakis, Spiliotis and Assimakopoulos, 2018). The practical lesson for a restaurant is to forecast at the level where it prepares food, using the drivers it knows in advance, not to invest in a more complex algorithm for a total forecast.

### 7.8.2 Reliability of the comparison

The controls in Chapter 3 make the comparison much more reliable than one where models get different information, but a 74 day test period gives limited statistical power. A non significant result, such as the difference between Prophet and the LSTM, means no evidence of a difference, not proof of equality. The rolling origin results reduce this worry, since an unstable order across windows is what similar true performance would give. The models also used fixed, sensible settings with similar effort for each, not heavy tuning, which on a test period this short would risk fitting its noise.

Two assumptions make some results a little optimistic. The A2 covariates and the item level inputs treat each day's promotions, events and weather as known in advance, which assumes good planning and a good weather forecast. As A2 was only slightly better than A1, this has little effect on the conclusions. The item level forecasts also cover the restaurant, menu item and day combinations recorded in the data, which a kitchen would know as its menu, assuming no sudden menu change.

### 7.8.3 Validity of the simulation

Of all the work, the simulation depends most on assumptions. Treating unsold portions as waste ignores reuse, and treating recorded sales as demand ignores sales limited by food running out, but both affect the two plans in similar ways. One margin for every row is simpler than a real kitchen would use, and the costs are estimates from the dataset. None of these assumptions clearly favours one plan. So the comparison between plans is more robust than their absolute levels, and the bootstrap intervals show that the advantage does not depend on a few unusual days. Above all, the simulation estimates overproduction, not food waste, which would need a trial in a working kitchen.

### 7.8.4 Generalisability

All results come from one dataset covering one year and 50 restaurants. Its origin cannot be confirmed, and some features, such as the random number of rows per day, are unusual for real sales data. So the findings are evidence about this dataset and the method, not a measurement of what forecasting would achieve in a given restaurant. The method itself transfers directly to other data, and the application can be retrained on a restaurant's own sales with one command.

## 7.9 Summary

For total daily demand, LSTM, Prophet and Random Forest worked about equally well with the same information and were only a little better than simple baselines. For item level demand, learned models, and gradient boosting in particular, were much and significantly better than the historical average rule. In simulation, the resulting preparation plan would have made about a third less overproduction while serving more demand. The application meets all its requirements. The main limits are the short test period, the use of simulation and not measured waste, and one dataset of uncertain origin.
