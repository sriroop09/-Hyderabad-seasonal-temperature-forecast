<div align="center">

# 🌡️ Seasonal Temperature Trend Analysis and 2030 Forecasting

**Hyderabad, Telangana, India**

How has each season in Hyderabad warmed since 2022, and how warm could it be by 2030?

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-3.0-150458?logo=pandas&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.7-F7931E?logo=scikitlearn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.64-FF4B4B?logo=streamlit&logoColor=white)

</div>

---

## 📌 Overview

This project turns **1,732 days** of Hyderabad temperature records into one average temperature per season per year. It then fits linear regression models to measure each season's warming trend and forecasts each season's average temperature for **2030**.

The results are shown in an interactive **Streamlit dashboard**.

![Seasonal trends](docs/figures/07_trends_all_seasons.png)

## 🔑 Key results

| Season | Months | Warming trend | Avg 2022–2026 | **2030 forecast** |
|---|---|---|---|---|
| ❄️ Winter | Dec – Feb | +0.37 °C / year | 23.39 °C | **25.55 °C** |
| ☀️ Summer | Mar – May | +0.42 °C / year | 29.65 °C | **32.19 °C** |
| 🌧️ Monsoon | Jun – Sep | +0.22 °C / year | 26.24 °C | **27.54 °C** |
| 🍂 Autumn | Oct – Nov | +0.34 °C / year | 24.34 °C | **26.55 °C** |

- **Every season warmed** between 2022 and 2026.
- **Summer** warmed fastest and **Monsoon** slowest.
- 2030 forecasts come from the Simple Linear Regression models (the main models).

## 🧮 Models

| | Simple Linear Regression (main) | Multiple Linear Regression (comparison) |
|---|---|---|
| Formula | `Temp = β₀ + β₁·Year` | `Temp = β₀ + β₁·Year + β₂·Summer + β₃·Monsoon + β₄·Autumn` |
| Number of models | 4 (one per season) | 1 (all seasons) |
| Trend | Each season has its **own** slope | All seasons **share one** slope (+0.34 °C/year) |
| Training points | 4–5 per model | 19 |

Season is one-hot encoded with **Winter as the baseline**. Models are evaluated with **R², MAE, MSE and RMSE**.

<details>
<summary><b>2030 forecast: Simple vs Multiple</b></summary>

| Season | Simple LR | Multiple LR |
|---|---|---|
| Winter | 25.55 °C | 25.34 °C |
| Summer | 32.19 °C | 31.68 °C |
| Monsoon | 27.54 °C | 28.28 °C |
| Autumn | 26.55 °C | 26.53 °C |

</details>

## 📊 Dataset

| | |
|---|---|
| File | `data/hyderabad_weather.xlsx` |
| Period | 30 Dec 2021 – 26 Sep 2026 (1,732 days) |
| Column used | `temperature_2m_mean` (daily mean temperature, °C) |
| Data quality | No missing values, no duplicates, no missing days |

**December counts toward the next year's Winter**, e.g. Dec 2021 + Jan–Feb 2022 = Winter 2022. Autumn 2026 is not in the data, because the data ends in September 2026.

## ⚙️ Workflow

```
Daily data  →  Assign seasons  →  Seasonal averages (19 points)
            →  Statistics & trend charts  →  Regression models
            →  Evaluation (R², MAE, MSE, RMSE)  →  2030 forecast  →  Streamlit app
```

## 🚀 Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 2. Install the requirements
pip install -r requirements.txt

# 3. Run the dashboard (opens at http://localhost:8501)
streamlit run app.py

# 4. (Optional) Open the full analysis notebook
jupyter notebook notebooks/temperature_analysis.ipynb
```

## 📁 Project structure

```
├── data/
│   └── hyderabad_weather.xlsx        # daily weather data
├── notebooks/
│   └── temperature_analysis.ipynb    # step-by-step analysis
├── docs/
│   ├── report.md                     # project report
│   ├── presentation_outline.md       # presentation slides outline
│   ├── viva_questions.md             # viva questions and answers
│   └── figures/                      # charts exported from the notebook
├── .streamlit/config.toml            # dashboard theme
├── app.py                            # Streamlit dashboard
├── model.py                          # analysis and model functions
└── requirements.txt
```

## 🌍 Environmental interpretation

The warming is consistent with factors common in fast-growing cities like Hyderabad:

- 🏙️ Urbanisation and the urban heat-island effect
- 🌳 Loss of green cover and water bodies
- 🏗️ Land-use change from open land to built surfaces
- ⚡ Rising energy use and cooling demand
- 🏭 Greenhouse-gas emissions and global warming

## ⚠️ Limitations

- Regression shows a **trend over time, not its cause**.
- Each trend is based on only **4–5 points** (2022–2026).
- 2030 is **4 years beyond the data**, so the forecasts are highly uncertain.
