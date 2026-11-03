# 8 Conclusion

## 8.1 Summary of the work

Using a public dataset of 10,000 sales records from 50 restaurants, this project compared forecasting models under controlled conditions in two tracks, turned the best forecasts into preparation plans and estimated their effects through simulation. It also built and tested an application that shows this to a restaurant manager.

## 8.2 Answers to the research questions

The first research question asked if LSTM, Prophet and Random Forest differ in forecasting total daily demand when given the same information. On this dataset, they do not. All three reached a WAPE of about 21 to 23 per cent and an R² of about 0.21 to 0.29. Most configurations were significantly better than the mean baseline, but no model was significantly better than the others. The rolling origin results put them within a fraction of a point of each other. The limit comes from the data. Much of the daily change in demand is caused by a factor that cannot be known in advance.

The second research question asked if a feature based model for each restaurant, menu item and day beats the historical average rule. It clearly does. Gradient boosting cut the error from 40.1 to 24.9 per cent WAPE and raised R² from 0.48 to 0.79. All four learned models were significantly better than the rule.

The third research question asked how much overproduction a plan using the best item level model would avoid in simulation. At the default safety margin of 10 per cent, it would avoid 34.1 per cent of the overproduction of a historical average plan (95 per cent interval 25.4 to 40.8 per cent) and serve 7.3 percentage points more of the demand. At an equal level of service it would avoid an optimistic 65.4 per cent (interval 61.3 to 68.8 per cent), optimistic because that margin was chosen on the test days. These are simulated estimates under stated assumptions, not measured reductions in waste.

The fourth research question asked if the methods could be delivered as a reliable and honest decision support application. They can. The application installs without an internet connection, starts on a fresh copy with reported system checks, passes all 90 automated tests, which cover its 23 requirements, and labels every estimate as an estimate.

## 8.3 Achievement of the objectives

Table 8.1 shows where each objective set in Chapter 1 was addressed and the evidence that it was met.

Table 8.1 Achievement of the objectives

| Objective | Where addressed | Evidence |
|---|---|---|
| O1 Review the literature on food service waste, forecasting, evaluation and decision support | Chapter 2 | Review of 41 verified sources and a statement of the gaps that the research questions address |
| O2 Analyse the dataset, its quality and the drivers of demand | Sections 3.4 to 3.6 | Quality checks, effect sizes of the demand drivers and the finding about records per day that shaped the design |
| O3 Design and run a controlled comparison with rolling origin checks and significance tests | Section 3.7, Sections 7.2 to 7.4 | Two tracks with equal information, rolling origin results and Diebold and Mariano tests for every model |
| O4 Convert forecasts into preparation plans and simulate their outcomes | Section 3.8, Section 7.5 | Simulation across margins from 0 to 20 per cent with bootstrap confidence intervals |
| O5 Specify, build and test a reliable web application | Chapters 4 to 6 | Requirements with priorities, working application, 90 passing tests and system tests on a fresh installation |
| O6 Evaluate the results critically | Section 7.8 | Discussion of statistical power, design asymmetries, simulation assumptions and generalisability |

## 8.4 Contributions

The project makes three modest contributions. The first is a worked example of how much a forecasting comparison's design can change its conclusion. On the same data, an item level model looks almost three times as accurate at daily level as the best time series model, when scored by summing its predictions over the rows that occurred. But a controlled comparison shows the models to be similar. The second is evidence, for this dataset, that machine learning adds value when it forecasts at the level of the preparation decision with the known drivers of demand, with an estimate of what that value would mean for overproduction and service. The third is a reproducible artefact. The application, offline pipeline, stored results, report figures and test evidence all come from the same code and data. So every number reported here can be reproduced and checked.

## 8.5 Limitations

The main limitations are discussed in Section 7.8. The 74 day test period limits the power of the significance tests. The overproduction results come from a simulation with stated assumptions, not from measured waste. All results come from a single dataset of uncertain origin that covers one year. The application was evaluated technically, not with users, because the project involved no human participants.

## 8.6 Future work

Several extensions would strengthen the conclusions. The most valuable would be a trial in a working kitchen, recording preparation quantities, sales and waste before and after the model based plan, so the simulated reduction could be tested against measured waste. Such a study would involve people and need ethical approval. On the modelling side, the forecasts could be made probabilistic, for example with quantile versions of gradient boosting. Then each item's preparation quantity could be set from its own costs, using the newsvendor logic discussed in Chapter 2, not from one margin for all items. Repeating the comparison on longer and better documented datasets would test if the findings generalise and allow yearly seasonality to be modelled. On the practical side, the application could be connected to a point of sale system. Sales would then be recorded automatically and the models retrained on a schedule. A usability evaluation with restaurant staff, again with ethical approval, would show if managers understand and trust what the application tells them.

## 8.7 Project management

### 8.7.1 Approach

The project was managed in the six timeboxed increments described in Section 3.3. They were ordered by risk, so the property most essential for assessment, an application that starts and runs, was secured first. Requirements were prioritised with MoSCoW. So if time ran short, Could have requirements would be dropped before any Must have requirement was affected. Each increment ended with the full test suite and a check on a fresh copy, so a working version ready to demonstrate existed at every stage.

### 8.7.2 Risks

Table 8.2 lists the main risks found during planning and how each was handled.

Table 8.2 Risk register

| Risk | Likelihood | Impact | Mitigation | Outcome |
|---|---|---|---|---|
| The application fails to start on the demonstration computer | Medium | High | SQLite instead of a database server, model training separated from serving, bundled packages, health checks, free port selection, self contained executable, tests on a fresh copy | Starts on a fresh copy in every test |
| Information from the test period leaks into training | Medium | High | Chronological split, history features from earlier days only, no record counts as inputs, unit tests of each rule | Leakage tests pass and detect an injected fault |
| Machine learning libraries fail to install | High | Medium | Libraries needed only offline, results shipped in a file | Application runs without them |
| Results overstated or misread | Medium | High | No accuracy figure, labelled estimates, significance tests, confidence intervals, honesty tests | All honesty tests pass |
| The data cannot answer a question as posed | Medium | Medium | Exploratory analysis before modelling, questions refined to what the data support | Two track design and simulation adopted |
| Time runs out before all features are complete | Medium | Medium | MoSCoW prioritisation and working increments | All Must and Should requirements delivered |

### 8.7.3 Response to feedback

The previous version of this work got detailed feedback, and this project was planned around it. Table 8.3 lists each point and where it was addressed.

Table 8.3 Response to feedback on the previous version

| Feedback | Action taken | Where |
|---|---|---|
| Food waste reduction was the central claim but was not measured | The claim was replaced by a simulation of overproduction with stated assumptions and confidence intervals, and the report states throughout that waste was not measured | Sections 1.6, 3.8, 7.5 |
| The feature based model was not compared like for like with the time series models | Two comparison tracks with equal information within each, two information sets, rolling origin checks, significance tests and an explanation of the earlier result | Sections 3.6, 3.7, 7.2 to 7.4 |
| The report described interviews and user feedback although the ethics approval stated there were no human participants | No people took part, the requirements were derived analytically, and every such reference was removed | Sections 1.7, 3.13, 4.2 |
| A value of 100 minus WAPE was labelled as accuracy | No accuracy figure is reported anywhere, and errors and R² are reported instead | Section 3.7.6 |
| A waste reduction figure from the literature appeared in the abstract as a result, and the abstract claimed the LSTM and Prophet comparison was not in the literature | The abstract reports only this project's results, literature figures are attributed to their sources, and the published comparisons are reviewed | Abstract, Sections 2.2, 2.5 |
| The server failed to start in the demonstration | The deployment was redesigned for a one click start without a database server, internet connection or machine learning libraries, and tested on a fresh copy | Sections 4.7, 5.4, 6.5 |
| Only some requirements were tested and evidence recorded only pass or fail | 90 automated tests record input, expected result and observed result, and all 23 requirements are traced to tests | Chapter 6, Appendices A and B |
| Some claims were too absolute and sources mixed research with blogs | The review uses verified academic and official sources only and states the gaps cautiously | Chapter 2 |
| The report relied on lists rather than argument and described the interquartile rule incorrectly | The report is written as argued prose, and the interquartile fences are defined from the quartiles | Throughout, Sections 2.8, 3.9 |

## 8.8 Reflection and learning outcomes

The most important lesson of the project is that an evaluation's design can matter more than the choice of model. The exploratory analysis was the turning point. Before the role of the number of records per day was understood, one model seemed far better than the others. Only careful attention to what each model could fairly know showed that the apparent advantage came from information, not the algorithm. A second lesson is that reliability and honesty are requirements to design and test, not qualities to hope for. Writing tests for the absence of an accuracy figure, or for the labels on simulated values, may seem unusual, but it ensured these properties held as the system changed.

Table 8.4 links the work to the learning outcomes of the individual project module.

Table 8.4 Learning outcomes

| Learning outcome | How it was demonstrated |
|---|---|
| Identify and outline a project | Problem statement, aim, objectives and research questions in Chapter 1 |
| Plan and carry out a project | Risk ordered increments, MoSCoW prioritisation and the risk register in Sections 3.3 and 8.7 |
| Conduct research at the front line of the subject | Literature review of forecasting, evaluation and decision support in Chapter 2 |
| Analyse project requirements | Use cases and requirements derived from the literature and the data in Chapter 4 |
| Produce a functional specification | Prioritised functional and non functional requirements, architecture, data model and interface in Chapter 4 |
| Critically evaluate a project | Significance tests, confidence intervals and the critical discussion in Chapter 7 |
| Demonstrate competence and originality | The two track controlled comparison, the simulation and the tested application in Chapters 3 to 6 |
| Present a project orally | Demonstration of the application, which starts with one click and was rehearsed on a fresh installation |

## 8.9 Concluding remarks

Reducing food waste in restaurants depends on many things that software cannot change, but better information about demand is one it can. This project found that, on the data available, the value of machine learning lay not in a more complex algorithm for total demand but in forecasting at the level where preparation decisions are made, using the drivers a restaurant already knows. When turned into a preparation plan, those forecasts would have cut overproduction a lot in simulation while serving more customers. Confirming that benefit in a working kitchen is the natural next step.
