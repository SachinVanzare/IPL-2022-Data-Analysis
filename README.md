# 🏏 IPL 2022 Data Analysis & Analytics Dashboard

An end-to-end data analysis project based on **IPL 2022 match-level data**.  
The project combines **Python, Pandas, NumPy, Plotly, Jupyter Notebook, and Streamlit** to analyze team performance, scoring patterns, player contributions, venue trends, toss outcomes, and winning margins.

## 📊 Project Overview

This project was developed as a data analytics capstone project to demonstrate the complete data analysis workflow:

**Data Understanding → Data Quality Assessment → Data Cleaning → Feature Engineering → Exploratory Data Analysis → KPI Analysis → Business Insights → Interactive Dashboard**

The original analysis was completed in a Jupyter Notebook and then converted into an interactive Streamlit dashboard for web-based exploration.

---

## 🎯 Project Objectives

The main objectives of this project are:

- Analyze IPL 2022 team performance
- Compare batting-first and chasing performance
- Study first-innings scoring patterns
- Analyze player contributions
- Identify venue-level scoring and match patterns
- Analyze toss decisions and toss-to-match conversion
- Examine winning margins
- Create business-style KPIs and insights
- Present the analysis through an interactive dashboard

---

## 🗂️ Dataset

The dataset contains **74 IPL 2022 matches** and **20 original columns**.

### Dataset includes:

- Match information
- Teams
- Venue
- Match stage
- Toss winner and toss decision
- First-innings score and wickets
- Second-innings score and wickets
- Match winner
- Winning method and margin
- Player of the Match
- Top scorer
- Highest score
- Best bowling performance
- Best bowling figures

The dataset covers **IPL 2022 only**.

---

## 🧹 Data Preparation

The analysis includes:

- Duplicate record checking
- Duplicate match ID validation
- Missing-value analysis
- Data-type validation
- Unique-value analysis
- Player-name consistency checks
- Team-name consistency checks
- Date cleaning
- Feature engineering
- Cleaning validation

Player-name inconsistencies were standardized where required, including:

- `K L Rahul` → `KL Rahul`
- `Suruakumar Yadav` → `Suryakumar Yadav`
- `Shardul Takur` → `Shardul Thakur`
- `R Aswin` → `R Ashwin`

---

## ⚙️ Feature Engineering

Additional analytical features were created from the original dataset, including:

- Month
- Month name
- Day name
- Weekend / Weekday classification
- Losing team
- Run-margin indicator
- Run margin
- Wicket margin
- Score difference
- First-innings team
- Second-innings team
- First-innings win indicator
- Parsed bowling wickets and runs

These features were used to support the KPI and exploratory analysis.

---

## 📈 Analysis Performed

### 🏆 Team Performance

The project analyzes:

- Matches played
- Matches won
- Matches lost
- Overall win rate
- Batting-first win rate
- Chasing win rate
- Group-stage performance
- Winning margins

### 🏏 Innings & Scoring Strategy

The analysis examines:

- First-innings scores
- Second-innings scores
- First-innings winning matches
- First-innings losing matches
- Score ranges
- Win rates by first-innings score range
- Batting-first vs chasing outcomes

### 👤 Player Performance

Player analysis includes:

- Player of the Match awards
- Top scorers
- Highest individual scores
- Best bowling performances
- Match-level player impact across selected dimensions

### 🏟️ Venue Analysis

The project examines:

- Matches played by venue
- Average first-innings score
- First-innings win rate
- Chasing win rate
- Winning margins

Venues with very small match samples are treated cautiously.

### 🪙 Toss Analysis

The project analyzes:

- Toss decision distribution
- Toss winner match-win rate
- Toss-to-match conversion by team
- Batting vs fielding decisions

### 📊 Advanced KPIs

Additional KPIs include:

- Overall team win rate
- Group-stage win rate
- Batting-first win rate
- Chasing win rate
- Run winning margins
- Wicket winning margins
- Toss conversion rate

---

## 💡 Key Findings

Based on the IPL 2022 dataset analyzed:

- **Gujarat recorded 12 wins from 16 matches**, giving a 75% overall win rate.
- Teams scoring **200+ runs in the first innings won 84.62% of matches** in this dataset.
- Matches with first-innings scores **below 140 had no first-innings wins** in this dataset.
- First-innings wins and chasing wins were evenly split at **37 matches each**.
- **Lucknow recorded an 87.50% batting-first win rate**.
- **Gujarat recorded an 88.89% chasing win rate**.
- Among regularly used venues, **Brabourne Stadium recorded the highest average first-innings score at 177.25 runs**.
- Toss winners won **36 of 74 matches**, resulting in a 48.65% toss-to-match conversion rate.
- **Kuldeep Yadav received 4 Player of the Match awards**.
- **Quinton de Kock recorded the highest individual score of 140** in the dataset.
- The largest recorded run-margin victory was **91 runs**.

> These findings describe associations observed in the IPL 2022 match-level dataset and should not be interpreted as proof of causation.

---

## 📊 Interactive Streamlit Dashboard

The project includes an interactive Streamlit dashboard with the following sections:

- 🏠 Overview
- 🏆 Team Performance
- 🏏 Innings & Strategy
- 👤 Player Performance
- 🏟️ Venue Analysis
- 🪙 Toss Analysis
- 💡 Key Insights
- 🔎 Data Explorer

The dashboard allows users to explore the cleaned dataset and visualize the major analytical findings interactively.

### 🚀 Live Dashboard

**Live Demo:**  
Coming soon — the dashboard will be deployed using Streamlit Community Cloud.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Data analysis and application development |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations and feature engineering |
| Plotly | Interactive visualizations |
| Matplotlib | Exploratory visualizations in the notebook |
| Jupyter Notebook | Data analysis and documentation |
| Streamlit | Interactive web dashboard |
| Git | Version control |
| GitHub | Source code hosting |

---

## 📁 Project Structure

```text
IPL-2022-Data-Analysis/
│
├── app.py
├── IPL.csv
├── requirements.txt
├── IPL_Capstone_Project.ipynb
├── .gitignore
└── README.md
```

---

## 💻 Run the Project Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Navigate to the project folder

```bash
cd IPL-2022-Data-Analysis
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Streamlit dashboard

```bash
streamlit run app.py
```

The application will open locally at:

```text
http://localhost:8501
```

---

## 🔬 Analytical Limitations

This project has several limitations:

- The dataset contains only IPL 2022 matches.
- The analysis is based on match-level data rather than ball-by-ball data.
- Some venues have very small sample sizes.
- Pitch and weather conditions are not included.
- Player availability and injury information are not included.
- The player impact analysis uses selected match-level dimensions rather than complete player statistics.
- Observed relationships represent associations within this dataset and do not establish causation.

---

## 👨‍💻 Project Author

**Sachin Vanzare**

B.Tech — Computer Science Engineering

### Skills Demonstrated

- Python
- Pandas
- NumPy
- Data Cleaning
- Feature Engineering
- Exploratory Data Analysis
- Data Visualization
- KPI Development
- Streamlit
- Git & GitHub

---

## ⭐ Project Highlights

This project demonstrates an end-to-end data analytics workflow, from raw match data to an interactive web dashboard.

**Raw Data → Clean Data → Feature Engineering → Analysis → KPIs → Insights → Interactive Dashboard**

If you find the project useful, feel free to ⭐ the repository.