# DSA210Project

# Graduate Admission Prediction using GradCafe Data Enriched with QS Rankings

## Project Overview
This project aims to build a predictive model that estimates the chance of graduate school admission based on applicant profiles collected from **TheGradCafe.com**. 

To enrich this dataset, I will be also using **QS World University Rankings by Subject 2025: Computer Science and Information Systems**. 

By combining applicant-level data with institutional quality metrics, this project seeks to identify the key factors that most strongly influence graduate admission outcomes and predict whether a student will be accepted to their target school. Moreover I believe that over a sginificant threshold, GPA doesn't have it's assumed impact on the applicaitons as it does under the threshold. I am intrested in finding the threshold.

---

## Motivation
As a Computer Sceince major who severly thinks about applying for a master's degree, the data I will examine through this project are what I am searching on regularly. I used to enjoy to watch an instagram acount called limmytalks. Limmy has around 1000 posts on evaluating applications of students for college and tyring to guess their results. I wish he would do the same content for masters applications too. But since he doesn't I will do my own masters limmytalks project. As I stated, I am searching for masters programs to apply and I usually compare myself to the student records I find in internet that accepted. At the end of this projects we will have a very detailed outcome of my chance for a masters program in Computer Science based on data rather than just surfing in internet.

This study also offers a practical contribution: it can serve as a transparent, data-backed tool for students making strategic decisions about where to apply, and for universities aiming to understand how their global standing correlates with acceptance trends.

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
  - Extract structured data fields (program, degree, GPA, decision, university, term, ethnicity...).
  - Export collected data.

### Step 2: Data Cleaning
- Remove rows with missing GPA or unclear decision results.
- Remove rows with missing ethnicity.
- Remove rows with decision= "Other on" since they usually are comments, suggestions... something that won't be related with my project.
- Standardize decision labels (“Accepted”, “Rejected”, “Waitlisted”).
- Normalize university names (case, punctuation, abbreviations).
- Handle missing GRE scores.

### Step 3: Data Enrichment
- Merge GradCafe dataset with QS dataset using approximate string matching since “UCLA”, “Univ. of California Los Angeles”, “University of California at LA” are acctualy all same.
- Convert qualitative ranks (“21+”, “201+”) into numeric bounds.
- Handle missing QS features.

### Step 4: Feature Engineering
- Encode categorical variables (degree type, term).
- Scale numerical features (GPA, ranking scores).
- Create binary target variable: `International = 1`, `American = 0`.

---

## Analysis Plan

### Exploratory Data Analysis (EDA)
- Visualize GPA and acceptance distributions.
- Analyze acceptance rates by program, term, and university tier.
- Examine correlations between QS indicators and acceptance outcomes.

### Statistical Analysis
- Evaluate whether GPA and university rank significantly affect admission outcomes.
- Use correlation matrices and chi-square tests for categorical relationships.
- **H: – GPA Saturation Hypothesis:**  Beyond a certain threshold (approximately GPA > 3.8), increases in GPA do not significantly increase the likelihood of acceptance.

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
- Balancing class distribution (more rejections than acceptances, more international than american appliciants).

---

## Tools and Technologies
- **Languages:** Python (pandas, numpy, selenium, fuzzywuzzy, scikit-learn, matplotlib, seaborn)
- **Data Collection:** Selenium
- **Analysis:** pandas, sklearn
- **Visualization:** seaborn, matplotlib
- **Version Control:** GitHub

---

## Limitations and Future Work
- GradCafe data may not represent all applicants (self-selection bias).
- Future work may integrate textual analysis of applicant comments or funding outcomes for deeper insights.



