@title Forecasting Restaurant Demand to Reduce Food Overproduction
@subtitle A Controlled Comparison of Forecasting Models and a Decision Support Application (EcoServe AI)
@author [Student name]
@studentid [Student ID]
@programme MSc [Programme title]
@module CMI3420 Individual Project
@supervisor Alok Verma
@school School of Computing and Engineering, University of Huddersfield
@date [Month and year of submission]

# Abstract

Restaurants make decisions on how much food to cook before they are sure how many people will be there. Usually, food that is prepared but not sold becomes garbage. This project addresses the question of whether, and at what level, machine learning forecasts give more than just basic rules for food preparation planning. Then it provides the method as a decision support application called EcoServe AI. All numbers are from an open dataset of 10,000 daily sales records from 50 restaurants and 14 menu items in 2024, which has no personal data. No human participants took part.

A quick examination of the data revealed that much of the variation in the total daily demand is due to the number of sales records there are for a particular day. This is an unknown quantity and cannot be predicted in advance. So the comparison is taken in two tracks, in which every model received the same information and was tested on the same 74 days that no model had seen. For total daily demand, all three models, LSTM, Prophet and Random Forest, predicted one day ahead using the same history data. Their weighted absolute percentage error (WAPE) was 20.7 to 22.8 per cent, compared to 26.3 per cent for a mean baseline. However, when they were given the same information, there was no significant difference between the models under the Diebold and Mariano test. For each restaurant, menu item and day, gradient boosting cut WAPE by 15.2 percentage points, from 40.1 per cent for the historical average rule to 24.9 per cent. It also raised R² from 0.48 to 0.79 (p < 0.001).

The data does not include the amount of waste, so the impact on waste was simulated. Replayed on the test period with a 10 per cent safety margin, a plan based on gradient boosting produced 34.1 per cent less overproduction than the plan that takes the historical average as the benchmark (95 per cent interval 25.4 to 40.8 per cent). It also met 7.3 percentage points more of the demand. These are estimated values under stated assumptions. They do not represent measured reductions in waste.

These results are displayed in an honest manner through the application. It begins with one click on a common laptop without any database server or machine learning libraries. It successfully passed all 90 automated tests that assess its 23 requirements. The main limitations are the short test period, the reliance on simulation and the use of a single dataset of uncertain origin.

**Keywords** demand forecasting, food waste, overproduction, restaurants, LSTM, Prophet, gradient boosting, forecast evaluation, decision support system

# Acknowledgements

I would like to thank my supervisor, Alok Verma, for his guidance and feedback. I thank the module leader, Mohd Zairul Mazwan Bin Jilani, and the School of Computing and Engineering at the University of Huddersfield, for the resources and support that made this project possible. I also thank Alexand Chen for publishing the dataset used in this work under an open licence.

# Abbreviations

| Abbreviation | Meaning |
|---|---|
| API | Application programming interface |
| CSV | Comma separated values (file format) |
| DSDM | Dynamic Systems Development Method |
| IQR | Interquartile range |
| JWT | JSON Web Token |
| LSTM | Long Short Term Memory network |
| MAE | Mean absolute error |
| MAPE | Mean absolute percentage error |
| MLP | Multilayer perceptron (neural network) |
| MoSCoW | Must have, Should have, Could have, Will not have this time |
| R² | Coefficient of determination |
| REST | Representational state transfer |
| RMSE | Root mean squared error |
| RQ | Research question |
| WAPE | Weighted absolute percentage error |
