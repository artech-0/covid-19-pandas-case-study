# Covid-19 Case Study

## Challenge Bounty
#### Cash Prize: **5K INR**
3-4 T-Shirts of *I Write Code* for other top submissions

## Begins
1st June, 2025

## Deadline
5th June, 2025

---

## Background
The COVID-19 pandemic, caused by the SARS-CoV-2 virus, emerged in late 2019 and rapidly spread globally, leading to significant health, economic, and social impacts. This unprecedented health crisis highlighted the crucial role of data analysis in managing such pandemics. By meticulously tracking and analyzing data on confirmed cases, recoveries, and deaths, policymakers and health professionals can make informed decisions to control the spread of the virus and allocate resources effectively.

---

## Dataset Details
This case study utilizes three key datasets, each providing daily updates on different aspects of the pandemic for various countries and regions:

*   **Confirmed Cases Dataset**: This dataset contains the cumulative number of confirmed COVID-19 cases per day for each country and region. The data spans from January 22, 2020, to May 29, 2021, with over 276 geographic entries.
*   **Deaths Dataset**: This dataset records the cumulative number of deaths attributed to COVID-19, structured similarly to the confirmed cases dataset. It provides crucial information for assessing the lethality and outbreak severity in different areas.
*   **Recovered Cases Dataset**: Includes data on the cumulative number of individuals who have recovered from COVID-19, which is vital for understanding the disease's progression and the effectiveness of treatment protocols.

Each dataset includes columns for **Province/State**, **Country/Region**, geographic coordinates (**Lat**, **Long**), and a series of dates representing daily cumulative totals.

---

## Objective of the Case Study
The primary objectives of this case study are:

*   **Practical Application of Python**: To demonstrate and enhance practical skills in using Python for data analysis, focusing on data manipulation, cleaning, and visualization.
*   **Insightful Data Analysis**: To provide analytical insights into the dynamics of COVID-19's spread, recovery, and mortality rates across different regions and over time.
*   **Skill Development**: To equip students with the knowledge to handle real-world data using Python libraries such as Pandas for data manipulation, Matplotlib and Seaborn for data visualization, and Numpy for numerical data processing.

---

## Data Analysis Problems

### Question 1: Data Loading
**Q1.1**: How do you load the COVID-19 datasets for confirmed cases, deaths, and recoveries into Python using Pandas?

### Question 2: Data Exploration
**Q2.1**: After loading the datasets, what is the structure of each dataset in terms of rows, columns, and data types?
**Q2.2**: Generate plots of confirmed cases over time for the top countries.
**Q2.3**: Generate plots of confirmed cases over time for China.

### Question 3: Handling Missing Data
**Q3.1**: Identify these missing values and replace them using a suitable imputation method, such as forward filling, for time-series data.

### Question 4: Data Cleaning and Preparation
**Q4.1**: Replace blank values in the province column with “All Provinces.”

### Question 5: Independent Dataset Analysis
**Q5.1**: Analyze the peak number of daily new cases in Germany, France, and Italy. Which country experienced the highest single-day surge, and when did it occur?
**Q5.2**: Compare the recovery rates (recoveries/confirmed cases) between Canada and Australia as of December 31, 2020. Which country showed better management of the pandemic according to this metric?
**Q5.3**: What is the distribution of death rates (deaths/confirmed cases) among provinces in Canada? Identify the province with the highest and lowest death rate as of the latest data point.

### Question 6: Data Transformation
**Q6.1**: Transform the 'deaths' dataset from wide format (where each column represents a date) to long format, where each row represents a single date, ensuring that the date column is in datetime format. How would this transformation be executed?
**Q6.2**: What is the total number of deaths reported per country up to the current date?
**Q6.3**: What are the top 5 countries with the highest average daily deaths?
**Q6.4**: How have the total deaths evolved over time in the United States?

### Question 7: Data Merging
**Q7.1**: How would you merge the transformed datasets of confirmed cases, deaths, and recoveries on the 'Country/Region' and 'Date' columns to create a comprehensive view of the pandemic's impact?
**Q7.2**: Analyze the monthly sum of confirmed cases, deaths, and recoveries for countries to understand the progression of the pandemic.[From the merged dataset]
**Q7.3**: Redo the analysis in Question 7.2 for the United States, Italy, and Brazil.

### Question 8: Combined Data Analysis
**Q8.1**: For the combined dataset, identify the three countries with the highest average death rates (deaths/confirmed cases) throughout 2020. What might this indicate about the pandemic's impact in these countries?
**Q8.2**: Using the merged dataset, compare the total number of recoveries to the total number of deaths in South Africa. What can this tell us about the outcomes of COVID-19 cases in the country?
**Q8.3**: Analyze the ratio of recoveries to confirmed cases for the United States monthly from March 2020 to May 2021. Which month experienced the highest recovery ratio, and what could be the potential reasons?