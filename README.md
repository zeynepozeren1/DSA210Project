# DSA210Project

# Graduate Admission Prediction 

## Project Overview
This project aims to build a predictive model that estimates the chance of graduate school admission based on applicant profiles collected from **TheGradCafe.com**. 

To enrich this dataset, I will be also using **QS World University Rankings by Subject 2025: Computer Science and Information Systems**. 

By combining applicant-level data with institutional quality metrics, this project seeks to identify the key factors that most strongly influence graduate admission outcomes and predict whether a student will be accepted to their target school. Moreover I believe that over a siginificant threshold, GPA doesn't have it's assumed impact on the applications as it does under the threshold. I am interested in finding the threshold.

---

## Motivation
As a Computer Sceince major who severly thinks about applying for a master's degree, the data I will examine through this project are what I am searching on regularly. I used to enjoy to watch an instagram account called limmytalks. Limmy has around 1000 posts on evaluating applications of students for college and trying to guess their results. I wish he would do the same content for masters applications too. But since he doesn't I will do my own masters limmytalks project. As I stated, I am searching for masters programs to apply and I usually compare myself to the student records I find in internet that accepted. At the end of this projects we will have a very detailed outcome of my chance for a masters program in Computer Science based on data rather than just surfing in internet.This personal motivation directly leads to the core research question of this project: whether GPA reaches a saturation point in admission decisions, and how institutional prestige interacts with applicant profiles.


---

## Data Sources

### 1. Applicant Data
- **Source:** TheGradCafe.com (https://www.thegradcafe.com/survey/?q=&sort=newest&institution=&program=Computer+Science&degree=Masters&season=&decision=&decision_start=&decision_end=&added_start=&added_end=)  
- **Description:** Crowdsourced reports of graduate school applications including: University name, Program, Degree type, GPA, GRE (where available), Decision status (Accepted / Rejected / Waitlisted), Admission term and season...

### 2. University Data (Data Enrichment)
- **Source:** QS World University Rankings by Subject 2025 — Computer Science & Information Systems (https://www.topuniversities.com/university-subject-rankings/computer-science-information-systems?tab=indicators&countries=us&sort_by=rank&order_by=asc)
- **Description:**  Publicly available dataset that provides university-level metrics such as Academic Reputation, Employer Reputation, Citations per Paper... These indicators quantify institutional quality and will be merged with GradCafe entries to enrich applicant-level data.


---

## Data Collection and Preprocessing


### Step 1: Web Scraping
- **Tool:** Selenium with ChromeDriver 
- **Process:**  
  - Automatically load each page of GradCafe results filtered for *Computer Science* and *Masters*.
  - Extract structured data fields (program, degree, GPA, decision, university, term, nationality...).
  - Export collected data.

### Step 2: Data Cleaning
- Remove rows with missing GPA or handle with mean/median.
- Remove rows with unclear decision results.
- Remove rows with missing nationality.
- Remove rows with decision= "Other on" since they usually are comments, suggestions... something that won't be related with my project.
- Standardize decision labels (“Accepted”, “Rejected”, “Waitlisted”).
- Normalize university names (case, punctuation, abbreviations).
- Handle missing GRE scores.

### Step 3: Data Enrichment
- Merge GradCafe dataset with QS dataset using approximate string matching since “UCLA”, “Univ. of California Los Angeles”, “University of California at LA” are actually all same.
- Convert qualitative ranks (“21+”, “201+”) into numeric bounds.
- Handle missing QS features.

### Step 4: Feature Engineering
- Encode categorical variables (degree type, term).
- Scale numerical features (GPA, ranking scores).
- Create binary target variable: `International = 1`, `American = 0`.

---

## Analysis Plan

### Exploratory Data Analysis (EDA)
- Examine overall data structure, missing values, duplicates, and outliers
- Visualize GPA, GRE, QS Rank, and other numerical features using histograms, density plots, and boxplots.
- Compare GPA and GRE distributions for accepted vs rejected applicants.
- Analyze the GPA to acceptance relationship with binned acceptance rates, moving averages, and non-linear smoothing to identify a potential GPA saturation threshold.
- Investigate QS Rank effects via scatterplots, rank bins, and Pearson/Spearman correlation analysis.
- Compare domestic vs international applicants across GPA, GRE, acceptance rates, and target school rank profiles.
- Explore temporal trends by examining acceptance rates, GPA trends, and QS Rank targets over application years.
- Conduct multivariate analysis using pairplots and correlation heatmaps to evaluate interactions among GPA, GRE, QS indicators, and outcomes.

### Hypotheses

- GPA SATURATION EFFECT
- Null Hypothesis (H0): Increases in GPA continue to significantly increase the probability of acceptance across the full GPA range.
- Alternative Hypothesis (H1): There exists a GPA threshold τ beyond which additional increases in GPA do not significantly increase the probability of acceptance.


- UNIVERSITY RANK INFLUENCE
- Null Hypothesis (H0): University QS Rank has no significant association with admission outcomes.
- Alternative Hypothesis (H1): University QS Rank is significantly associated with admission outcomes, such that better-ranked universities exhibit higher acceptance probabilities.

### Statistical Analysis

- Test whether GPA and university QS Rank significantly influence admission outcomes in alignment with the project’s two main hypotheses.
- Apply piecewise logistic regression and changepoint detection methods to evaluate the GPA Saturation Hypothesis and statistically estimate the threshold τ, where increases in GPA no longer contribute meaningfully to acceptance probability.
- Use generalized additive models (GAM) or non-linear smoothing techniques to examine whether the GPA–acceptance curve flattens beyond the threshold τ.
- Analyze the impact of university prestige by evaluating the relationship between QS Rank and admission outcomes using logistic regression coefficient significance tests and Spearman rank correlation.
- Perform chi-square tests of independence for categorical comparisons when appropriate, following the course’s hypothesis-testing framework.
- Report p-values, confidence intervals, and effect sizes, and make decisions on rejecting or failing to reject each null hypothesis under a standard significance level (α = 0.05).

### Predictive Modeling
- Develop classification models to predict admission results.
- Possible Algorithms: Logistic Regression, Random Forest, XGBoost etc.
- Evaluate with accuracy, precision-recall, F1 score, and ROC-AUC.
- Use SHAP analysis to interpret feature importance and model decisions.

### Deliverables
- Cleaned and merged dataset
- EDA visualizations
- Trained predictive models
- Model interpretability analysis
- Final written report and GitHub repository with documentation

---

## Expected Challenges
- Name inconsistencies between GradCafe and QS data.
- Missing or biased user-reported entries on GradCafe.
- Balancing class distribution (more rejections than acceptances, more international than american applicants).

---

## Tools and Technologies
- **Languages:** Python (pandas, numpy, selenium, fuzzywuzzy, scikit-learn, matplotlib, seaborn)
- **Data Collection:** Selenium
- **Analysis:** pandas, sklearn
- **Visualization:** seaborn, matplotlib
- **Version Control:** GitHub

---

## Limitations and Future Work
- GradCafe data may not represent all applicants.
- Future work may integrate textual analysis of applicant comments or funding outcomes for deeper insights.



