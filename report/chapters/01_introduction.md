# 1 Introduction

## 1.1 Context

Every morning, restaurants make decisions on how many portions of each dish to prepare. They do this long before they know how many customers will come. When they cook too little, their guests are not happy and the restaurant loses money. When they cook too much, the leftovers are often wasted, since it is not possible to store cooked food safely for long. So in the food service sector, food waste is partly a forecasting problem. The waste that comes from preparing more than is sold is the portion that a restaurant can control most directly (Papargyropoulou et al., 2016).

Food service is estimated to be one of the primary contributors of food waste globally (United Nations Environment Programme, 2024). Research on individual businesses indicates that much of the purchased food never reaches a customer (Betz et al., 2015). Reducing that share needs many actions, but better information about expected demand is one of the few actions that software can give at low cost.

Machine learning provides means of creating this information. Demand can be forecast with recurrent neural networks, for instance the Long Short Term Memory network (Hochreiter and Schmidhuber, 1997). It can also be forecast with time series models that divide a series into components, like Prophet (Taylor and Letham, 2018), and with tree ensembles such as Random Forest (Breiman, 2001) and gradient boosting (Friedman, 2001). Numerous comparisons have been made between their strengths. Evidence indicates that the answer highly depends on the data. It also depends on the level at which the demand is forecast, and on how fairly the comparison is set up (Makridakis, Spiliotis and Assimakopoulos, 2018). A forecast isn't helpful unless it influences a decision. A model that is a little more accurate on paper is not of much value unless it results in amounts of preparation that waste less food and still serve all customers.

This project is dubbed EcoServe AI and addresses both sides of the problem. It provides a comparison of forecasting techniques under controlled conditions on a public restaurant sales dataset. It also turns the forecasts into preparation plans and uses simulation to estimate their impact on overproduction. Last but not least, it provides the results through a web based decision support application that a restaurant manager might use.

## 1.2 Problem statement

Three problems motivate the project. The first is about method. Comparisons between forecasting models are easy to make unfair. For example, one model may get richer inputs than another, models may forecast at different levels of detail, or information from the test period may leak into training (Kaufman et al., 2012). Then a difference in reported error says more about the experiment design than about the algorithms. So conclusions about which model to use cannot be trusted.

The second problem is about the link between forecasting and waste. Most public sales datasets, including the one used here, record what was sold but not what was prepared or thrown away. So a claim that a forecasting system reduces waste cannot be tested by measuring waste directly. It can only be studied by stating clear assumptions about how forecasts become preparation decisions. Then the results of those decisions are estimated on data that the models have never seen.

The third problem is practical. Forecasting research often ends with a table of error metrics, but a manager needs a tool that runs reliably, shows results honestly and is easy to understand for people who did not build it (Arnott and Pervan, 2014).

## 1.3 Aim

The aim of the project is to find out, on public restaurant sales data, whether machine learning forecasts do better than simple rules for planning food preparation and at which level. It also aims to deliver the resulting method as a reliable decision support application that reports its evidence honestly.

## 1.4 Objectives

The aim is split into six objectives. The first objective (O1) is to review the literature on food service waste, demand forecasting, forecast evaluation and decision support. This finds suitable models, metrics and evaluation methods. The second objective (O2) is to analyse the public dataset, its quality and what drives demand in it, and to find which forecasting tasks it can support. The third objective (O3) is to design and run a controlled comparison where every model within a task gets the same information and is tested on the same unseen days. It also uses rolling origin checks and significance tests. The fourth objective (O4) is to turn forecasts into preparation plans. It then uses a simulation with stated assumptions to estimate how much overproduction and unmet demand each plan would cause. The fifth objective (O5) is to specify, build and test a web application that shows the results, supports routine data entry and starts reliably on an ordinary laptop. The sixth objective (O6) is to evaluate the results critically, including their statistical reliability, their validity and the limits that the data put on them.

## 1.5 Research questions

Four research questions guide the work. RQ1 asks whether LSTM, Prophet and Random Forest differ in how well they forecast total daily restaurant demand when they get the same information. RQ2 asks whether a feature based model that forecasts demand for each restaurant, menu item and day does better than the historical average rule. A restaurant might use this rule without any model. RQ3 asks how much overproduction a preparation plan from the best item level model would avoid. The comparison is with a plan based on the historical average, and both plans are replayed on unseen days in a simulation. RQ4 asks whether these methods can be delivered as a decision support application that starts reliably, meets its requirements and reports results without overstating them.

## 1.6 Scope

The project uses one public dataset of restaurant sales, described in Chapter 3, which covers 50 restaurants and 14 menu items over the year 2024. The forecasting comparison works at two levels of detail. These are the total demand of all restaurants per day and the demand for each restaurant, menu item and day. Waste is not measured anywhere in the dataset, so the project estimates overproduction through simulation, and it does not claim to have measured a fall in food waste. The application is a working prototype for a single site. It runs locally and stores data in a file based database. It serves forecasts that an offline pipeline calculated in advance. Outside the scope of this project are links with point of sale systems, live use in a restaurant and studies with restaurant staff.

## 1.7 Data and ethics

All data come from a public secondary dataset published on Kaggle under the Creative Commons Attribution ShareAlike 4.0 licence (Chen, 2025). The dataset contains sales figures, prices, promotions, events and weather conditions. It contains no information about any person. No people took part in the project. No interviews, surveys or user trials were done, and no personal data were collected or processed. So the project had no human participants, and this matches its ethics approval. As its licence requires, the dataset is credited in the application and in this report. The work also follows the professional standards set out in the BCS Code of Conduct (BCS, n.d.).

## 1.8 Structure of the report

Chapter 2 reviews the literature on food service waste, demand forecasting, forecast evaluation, preparation decisions, anomaly detection and decision support. It also shows the gaps that the research questions deal with. Chapter 3 explains the research design, the dataset and its quality, the controlled comparison, the preparation simulation and the development approach. Chapter 4 sets out the requirements and the design of the application. Chapter 5 describes its implementation. Chapter 6 presents the testing strategy and the evidence from the automated test suite. Chapter 7 reports the results of the comparison and the simulation, evaluates them critically and answers the research questions. Chapter 8 concludes the report, discusses limitations and future work, and reflects on how the project was managed.
