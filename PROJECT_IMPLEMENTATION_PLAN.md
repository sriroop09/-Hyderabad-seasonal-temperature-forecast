# PROJECT IMPLEMENTATION PLAN

## Seasonal Temperature Trend Analysis and 2030 Forecasting — Hyderabad, Telangana, India

---

## Project Overview

**What the project does:**
The project converts daily Hyderabad temperature records into one average temperature per season per year, describes each season with descriptive statistics, and plots how each season changes from year to year. It then builds two kinds of regression:

- **Four Simple Linear Regression models**, one per season (X = Year, Y = seasonal average temperature)
- **One Multiple Linear Regression model** trained on all seasons together (X = Year + Season, Y = seasonal average temperature)

Both approaches are evaluated and used to forecast each season's average temperature for 2030. Results are presented in a simple Streamlit app and documented in a README, report and PPT.

**Location:** Hyderabad, Telangana, India (single city, fixed)

**Dataset:** `hyderabad_weather_checked_cleaned.xlsx`, a daily weather dataset. The main column is `temperature_2m_mean`.

**Historical period:** The raw data covers 30 Dec 2021 to 26 Sep 2026. The seasonal modelling table covers 2022–2026 (see the findings below).

**Main ML methods (sklearn `LinearRegression` only):**
- 4 × Simple Linear Regression: Year → seasonal average temperature (one model per season)
- 1 × Multiple Linear Regression: Year + Season (one-hot encoded) → seasonal average temperature

**Final output:**
- Seasonal statistics tables
- Four seasonal trend line charts
- Model evaluation tables (R², MAE, MSE, RMSE) for both approaches
- 2030 seasonal forecast table showing Simple and Multiple regression forecasts side by side
- Environmental interpretation, including the causation limitation
- Streamlit app
- README, report and PPT

---

## What the Dataset Actually Contains (verified by read-only inspection)

| Item | Finding |
|---|---|
| Sheets | 1 (`Sheet1`) |
| Rows × Columns | 1,732 × 14 |
| Date column | `date` (already datetime) |
| City column | `city`, always "Hyderabad" |
| Main temperature column | `temperature_2m_mean` (float) |
| Other columns (not used) | `temperature_2m_max`, `temperature_2m_min`, `apparent_temperature_max`, `precipitation_sum`, `precipitation_hours`, `relative_humidity_2m_mean`, `wind_speed_10m_max`, `wind_direction_10m_dominant`, `shortwave_radiation_sum`, `et0_fao_evapotranspiration`, `weather_code` |
| Missing values | 0 |
| Duplicate rows / dates | 0 |
| Missing calendar days | 0 |
| Date range | 2021-12-30 to 2026-09-26 |
| `temperature_2m_mean` range | 18.7 °C to 34.9 °C (plausible) |

### Three findings that shape the plan

**1. 2021 contains only 2 days (30–31 December).**
No full 2021 season can be formed without inventing data, so the modelling table starts at 2022.

**2. Winter crosses the year boundary.**
This plan uses the standard meteorological convention: December belongs to the *next* year's winter.
Example: Dec 2021 + Jan 2022 + Feb 2022 = **Winter 2022**.

**3. 2026 is incomplete.**
- Monsoon 2026 has 26 of 30 September days. It is included, and this is documented.
- Autumn 2026 (Oct–Nov) does not exist in the data, so it is excluded.

### Resulting data points

| Season | Months | Years | Points |
|---|---|---|---|
| Winter | Dec, Jan, Feb | 2022–2026 | 5 |
| Summer | Mar, Apr, May | 2022–2026 | 5 |
| Monsoon | Jun, Jul, Aug, Sep | 2022–2026 | 5 |
| Autumn/Post-monsoon | Oct, Nov | 2022–2025 | 4 |
| **All seasons (Multiple Regression)** | | | **19** |

**Important limitations (to be stated in the notebook, app, report and viva):**
- Each simple model is trained on only 4–5 points. The multiple model uses 19 points, which is still small.
- A train/test split is not meaningful at this size, so metrics are calculated on the training points (in-sample evaluation).
- The 2030 forecast extrapolates 4 years beyond the data, so it carries high uncertainty.
- Regression shows a statistical relationship with Year. It does not prove causation.

---

## Simple vs Multiple Regression in This Project

| | Simple Linear Regression | Multiple Linear Regression |
|---|---|---|
| Number of models | 4 (one per season) | 1 (all seasons together) |
| Inputs (X) | Year | Year, Season_Summer, Season_Monsoon, Season_Autumn |
| Training rows | 4–5 per model | 19 |
| Equation | Temp = β₀ + β₁·Year | Temp = β₀ + β₁·Year + β₂·Summer + β₃·Monsoon + β₄·Autumn |
| Trend (slope) | Each season has its **own** slope | All seasons **share one** slope |
| Seasonal level | Separate intercept per model | Winter is the baseline; dummy coefficients are offsets from Winter |

**Why Winter is the baseline:** With 4 seasons, only 3 dummy columns are used (`drop_first`). Including all 4 would cause perfect multicollinearity (the *dummy variable trap*), because the four columns always sum to 1.

**Viva one-liner:** "Simple regression estimates a separate trend for each season. Multiple regression estimates one shared yearly trend while using Season to adjust the temperature level."

---

## Project Structure

```
temperature-forecasting/
│
├── data/
│   └── hyderabad_weather.xlsx
│
├── notebooks/
│   └── temperature_analysis.ipynb
│
├── app.py
├── model.py
├── requirements.txt
└── README.md
```

**Role of each file:**
- `notebooks/temperature_analysis.ipynb`: step-by-step analysis with explanations. This is the main academic record.
- `model.py`: small reusable functions (load, assign season, aggregate, statistics, train simple models, train multiple model, evaluate, forecast) that the Streamlit app imports.
- `app.py`: the simple Streamlit display layer.
- `README.md`: project documentation.
- `requirements.txt`: Python dependencies.

---

## Day Overview

The plan now has **8 days**. Multiple regression gets its own day so that no single day holds too many major tasks.

| Day | Focus |
|---|---|
| 1 | Setup, inspection, data verification |
| 2 | Season classification and seasonal aggregation |
| 3 | Descriptive statistics and trend graphs |
| 4 | Four Simple Linear Regression models |
| 5 | Multiple Linear Regression model |
| 6 | Model evaluation and 2030 forecasting (both approaches) |
| 7 | Environmental interpretation and Streamlit app |
| 8 | Testing, README, report and PPT |

---

## DAY 1 — Project Setup, Dataset Inspection & Data Verification

### 1. Goal of the Day
Set up the project folder and environment, load the Excel file, and formally verify data quality, so that we can state with evidence whether any cleaning was needed.

### 2. Concepts We Will Learn
- Project folder structure and virtual environments
- Reading Excel files with pandas (`read_excel`, openpyxl engine)
- Data types (datetime, float, string)
- Data quality checks: missing values, duplicates, date validity, value plausibility
- Date continuity in a daily time series

### 3. Exact Tasks
1. Create the `temperature-forecasting/` folder with `data/` and `notebooks/` subfolders.
2. Copy the uploaded file into `data/` and rename it `hyderabad_weather.xlsx`.
3. Create a virtual environment.
4. Write `requirements.txt` with pandas, numpy, matplotlib, scikit-learn, openpyxl, streamlit and jupyter.
5. Install the requirements.
6. Create `temperature_analysis.ipynb` and load the dataset.
7. Inspect the data: `shape`, column names, `dtypes`, `head()`, `tail()`.
8. Run the verification checks:
   - Missing values per column
   - Duplicate rows and duplicate dates
   - `date` has datetime type; min and max dates
   - Date continuity (compare against a full daily calendar)
   - `city` contains only "Hyderabad"
   - `temperature_2m_mean` is numeric and within a plausible range
   - Row consistency: `temperature_2m_min` ≤ `temperature_2m_mean` ≤ `temperature_2m_max`
9. Build a days-per-year-per-month table to confirm the partial 2021 and 2026 coverage.
10. Write a "Data Verification Summary" markdown cell.

### 4. Files to Create/Modify
- `data/hyderabad_weather.xlsx` (copied)
- `requirements.txt` (created)
- `notebooks/temperature_analysis.ipynb` (created; Day 1 section)

### 5. Input
- The uploaded Excel file

### 6. Output
- The complete folder structure
- A working Python environment
- A notebook section with all verification results and a written summary

### 7. Code Work
- Import libraries and load the Excel file with pandas.
- Write one short check per verification item (`isna().sum()`, `duplicated()`, a `pd.date_range` comparison, a boolean min ≤ mean ≤ max check, `describe()`).
- Build a pivot or group-by table of day counts per year and month.

### 8. Validation
- The file loads without errors.
- 1,732 rows and 14 columns.
- Date range is 2021-12-30 to 2026-09-26.
- 0 missing values, 0 duplicates, 0 missing dates.
- Mean temperatures fall within roughly 18–35 °C.

### 9. Expected Result
All checks pass. The summary cell states: "No cleaning was required." It also documents the coverage limits (only 2 days in 2021; data ends 26 Sep 2026).

### 10. Stopping Point
Stop after the Data Verification Summary is written. Do not create season columns yet.

---

## DAY 2 — Date Processing, Season Classification & Seasonal Aggregation

### 1. Goal of the Day
Assign every day to one of the four seasons with the correct season year, then build the final modelling table: **Year | Season | Average Temperature**.

### 2. Concepts We Will Learn
- Extracting month and year from dates
- Mapping categorical values (month → season)
- The season-year problem for Winter (December belongs to the next year's winter)
- Group-by aggregation (split–apply–combine)
- Data completeness and why partial seasons matter

### 3. Exact Tasks
1. Keep only `date` and `temperature_2m_mean` for the analysis.
2. Create a `Month` column from `date`.
3. Create a `Season` column using exactly these four seasons:
   - Winter: Dec, Jan, Feb
   - Summer: Mar, Apr, May
   - Monsoon: Jun, Jul, Aug, Sep
   - Autumn: Oct, Nov
4. Create a `Season_Year` column: calendar year for all months, except December, which gets year + 1.
5. Count the days in each (Season_Year, Season) group.
6. Apply the completeness rules:
   - Keep all seasons from 2022–2026 that exist in the data.
   - Monsoon 2026 is kept with a documented note (26 of 30 September days).
   - Autumn 2026 does not exist, so no row is created.
7. Group by Season_Year and Season, and calculate the mean of `temperature_2m_mean`.
8. Rename the columns to `Year`, `Season`, `Average_Temperature`.
9. Order the seasons as Winter → Summer → Monsoon → Autumn within each year.
10. Display the final seasonal table (expected 19 rows).
11. Move the season-assignment and aggregation logic into functions in `model.py`.

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 2 section)
- `model.py` (created; first functions: `load_data`, `assign_season`, `build_seasonal_table`)

### 5. Input
- `data/hyderabad_weather.xlsx`
- The Day 1 notebook section

### 6. Output
- A daily DataFrame with `Month`, `Season` and `Season_Year` columns
- A day-count table per season-year
- The final seasonal modelling table (Year | Season | Average_Temperature)
- `model.py` with the first reusable functions

### 7. Code Work
- A month-to-season mapping (dictionary)
- Season-year logic using a simple condition for December
- `groupby(...).mean()` and `groupby(...).size()` for averages and day counts
- Wrapping the logic into small, well-named functions in `model.py`

### 8. Validation
- Every row has exactly one season; no unassigned months.
- Dec 2021 rows are labelled Winter 2022.
- Expected day counts:
  - Winter 2022: 61 (2 + 31 + 28)
  - Winter 2023, 2025, 2026: 90 each
  - Winter 2024: 91 (leap-year February)
  - Summer: 92 per year
  - Monsoon: 122 per year, except 2026 with 118
  - Autumn: 61 per year (2022–2025)
- The final table has 19 rows with no 2021 row and no Autumn 2026 row.
- Summer and Monsoon averages are higher than Winter, which is physically sensible.

### 9. Expected Result
A clean 19-row table, for example:

| Year | Season | Average_Temperature |
|---|---|---|
| 2022 | Winter | xx.xx |
| 2022 | Summer | xx.xx |
| 2022 | Monsoon | xx.xx |
| 2022 | Autumn | xx.xx |
| … | … | … |
| 2026 | Monsoon | xx.xx |

This single table feeds **both** regression approaches: the simple models use it filtered by season; the multiple model uses all 19 rows.

### 10. Stopping Point
Stop after the seasonal table is created and validated, and the functions are in `model.py`. No statistics or graphs yet.

---

## DAY 3 — Descriptive Statistics, Exploratory Analysis & Seasonal Trend Graphs

### 1. Goal of the Day
Describe each season statistically and visualise how each season's average temperature changes across years.

### 2. Concepts We Will Learn
- Measures of central tendency: mean, median
- Measures of spread: minimum, maximum, variance, standard deviation
- Sample variance vs population variance (pandas uses sample variance, `ddof=1`)
- Why seasonal statistics are calculated from daily values
- Line charts for trends; box plots for distributions

### 3. Exact Tasks
1. **Table 1 (Seasonal descriptive statistics):** For each season, calculate the mean, median, minimum, maximum, variance and standard deviation of daily `temperature_2m_mean` across the full period.
2. Round the values to 2 decimals and order the seasons Winter → Summer → Monsoon → Autumn.
3. **Table 2 (Year-wise seasonal averages):** Pivot the Day 2 table into Years × Seasons for easy reading.
4. Create a bar chart of the mean temperature per season.
5. Create a box plot of daily temperatures grouped by season.
6. Create four seasonal trend line charts (Winter, Summer, Monsoon, Autumn): X-axis = Year, Y-axis = Average seasonal temperature (°C), with markers on each point.
7. Write short observations under each chart: which season is hottest, which varies most, and whether each trend looks upward, downward or flat.
8. Add a `seasonal_statistics` function and a trend-plot helper to `model.py`.

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 3 section)
- `model.py` (add the statistics and plotting helper functions)

### 5. Input
- The daily DataFrame with seasons (Day 2)
- The seasonal modelling table (Day 2)

### 6. Output
- The seasonal descriptive statistics table
- The year-wise seasonal averages table
- One bar chart and one box plot
- Four seasonal trend line charts
- Written observations

### 7. Code Work
- `groupby('Season')` with `agg` for the six statistics
- `pivot` for the Years × Seasons table
- matplotlib plotting: bar chart, box plot, four line charts with titles, axis labels and integer-only year ticks
- Helper functions in `model.py` so the app can reuse them

### 8. Validation
- For each season: min ≤ median ≤ max, and min ≤ mean ≤ max.
- Standard deviation equals the square root of the variance.
- Summer should show the highest mean and Winter the lowest (or close to it).
- Each trend chart has the correct number of points (5, or 4 for Autumn).
- Year ticks show whole years only (no 2022.5).

### 9. Expected Result
A readable statistics table and clear, labelled charts. The trend charts are simple lines with 4–5 points each. Observations are cautious ("appears slightly increasing"), not overstated.

### 10. Stopping Point
Stop after all tables, charts and observations are complete. No regression yet.

---

## DAY 4 — Simple Linear Regression Models (4 models)

### 1. Goal of the Day
Train four separate Simple Linear Regression models, one per season, using Year as X and seasonal average temperature as Y. Interpret the slope and intercept of each.

### 2. Concepts We Will Learn
- Simple Linear Regression: Y = β₀ + β₁X
- Least squares estimation
- Meaning of the slope (°C change per year) and intercept
- Why the model uses seasonal averages rather than daily observations
- sklearn workflow: `fit`, `predict`, `coef_`, `intercept_`
- Why X must be 2-dimensional in sklearn
- Why there is no train/test split with only 4–5 points

### 3. Exact Tasks
1. For each season, filter the seasonal table to that season.
2. Set X = `Year` (2-D) and Y = `Average_Temperature`.
3. Fit a `LinearRegression` model for each season.
4. Record the slope and intercept of each model.
5. Write the regression equation for each season.
6. Calculate fitted values for the historical years.
7. Plot actual seasonal averages with the fitted regression line, one plot per season.
8. Interpret each slope in plain words, e.g. "Winter average temperature changes by about +0.xx °C per year in this data."
9. Add a markdown note: "Trends come from very few points; interpret with caution."
10. Add a `train_simple_models` function to `model.py` that returns the four fitted models.

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 4 section)
- `model.py` (add `train_simple_models`)

### 5. Input
- The seasonal modelling table (Day 2)

### 6. Output
- Four trained Simple LinearRegression models
- A coefficients table (Season | Slope | Intercept | Equation)
- Four "actual vs fitted line" plots
- Written slope interpretations

### 7. Code Work
- A loop over the four seasons that fits one `LinearRegression` each
- Storing the models in a dictionary keyed by season
- Building a coefficients table from `coef_` and `intercept_`
- matplotlib scatter points plus the fitted line per season

### 8. Validation
- Exactly four models exist, and each was trained only on its own season's rows.
- Training sizes: 5, 5, 5, 4.
- Slopes are small (fractions of a °C per year). A slope of several °C per year would indicate a bug.
- The fitted line passes through the "middle" of the points on each plot.
- As a sanity check, the slope from sklearn matches `numpy.polyfit(X, Y, 1)` for one season.

### 9. Expected Result
A coefficients table with four rows, for example:

| Season | Slope (°C/year) | Intercept | Equation |
|---|---|---|---|
| Winter | ±0.xx | … | Temp = … + 0.xx × Year |
| … | … | … | … |

Plus four simple regression plots with plain-language interpretations.

### 10. Stopping Point
Stop after the four simple models are trained and interpreted. No multiple regression, metrics or forecasts yet.

---

## DAY 5 — Multiple Linear Regression Model (Year + Season)

### 1. Goal of the Day
Train one Multiple Linear Regression model on all 19 seasonal rows, using Year and Season (one-hot encoded) as inputs, and interpret its coefficients.

### 2. Concepts We Will Learn
- Multiple Linear Regression: Y = β₀ + β₁X₁ + β₂X₂ + … + βₖXₖ
- Categorical variables and one-hot (dummy) encoding
- The dummy variable trap and why one category is dropped
- Reference (baseline) category: Winter
- Interpreting coefficients "holding other variables constant"
- Shared-slope assumption: one Year trend for all seasons
- How this differs from the four separate simple models

### 3. Exact Tasks
1. Start from the full 19-row seasonal table.
2. Set Season as an ordered categorical (Winter, Summer, Monsoon, Autumn) so that Winter is the dropped baseline.
3. One-hot encode Season with `pd.get_dummies(..., drop_first=True)`, creating `Season_Summer`, `Season_Monsoon` and `Season_Autumn`.
4. Build X = [`Year`, `Season_Summer`, `Season_Monsoon`, `Season_Autumn`] and Y = `Average_Temperature`.
5. Fit one `LinearRegression` model.
6. Build a coefficients table (Feature | Coefficient) plus the intercept.
7. Write out the full regression equation.
8. Interpret each coefficient:
   - `Year`: estimated °C change per year, shared by all seasons
   - `Season_Summer`: how much warmer Summer is than Winter in the same year, on average
   - `Season_Monsoon` and `Season_Autumn`: the same, relative to Winter
9. Calculate fitted values for all 19 rows.
10. Plot actual seasonal averages with the four fitted lines. The lines will be parallel, which visually shows the shared slope.
11. Write a short comparison: the Year coefficient from the multiple model vs the four separate slopes from Day 4.
12. Add a `train_multiple_model` function to `model.py` (including the encoding step, so 2030 inputs are encoded the same way).

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 5 section)
- `model.py` (add `train_multiple_model` and a small `encode_features` helper)

### 5. Input
- The seasonal modelling table (Day 2)
- The Day 4 simple-model slopes (for comparison)

### 6. Output
- One trained Multiple LinearRegression model
- A coefficients table and full equation
- A plot of actual points with four parallel fitted lines
- A written interpretation and a simple-vs-multiple comparison

### 7. Code Work
- `pd.Categorical` to fix the season order
- `pd.get_dummies(drop_first=True)` for encoding
- One `LinearRegression().fit(X, y)` call
- Building a coefficients table from `coef_` and `feature_names`
- matplotlib plot with the four fitted lines

### 8. Validation
- X has shape (19, 4), with no `Season_Winter` column.
- Each row has at most one dummy equal to 1; Winter rows have all three dummies = 0.
- The Year coefficient is small (fractions of a °C per year).
- The dummy coefficients match the pattern seen on Day 3. For example, if Summer is several °C warmer than Winter, `Season_Summer` is several °C and positive.
- The four fitted lines on the plot are parallel.
- A manual check for one row: intercept + β₁·Year + (relevant dummy coefficient) equals `model.predict` for that row.

### 9. Expected Result
A coefficients table, for example:

| Feature | Coefficient |
|---|---|
| Intercept | … |
| Year | ±0.xx |
| Season_Summer | +x.xx |
| Season_Monsoon | +x.xx |
| Season_Autumn | ±x.xx |

Plus a plot with four parallel lines and a short paragraph explaining what "Winter as baseline" and "shared slope" mean.

### 10. Stopping Point
Stop after the multiple model is trained, interpreted and compared with the simple slopes. No metrics or 2030 forecasts yet.

---

## DAY 6 — Model Evaluation & 2030 Forecasting (Simple and Multiple)

### 1. Goal of the Day
Evaluate the four simple models and the multiple model with R², MAE, MSE and RMSE, then forecast the 2030 average temperature for each season using both approaches.

### 2. Concepts We Will Learn
- Residuals (actual − predicted)
- R² (coefficient of determination): the share of variance explained
- MAE: average absolute error in °C
- MSE: average squared error
- RMSE: square root of MSE, back in °C
- In-sample evaluation and its limitations
- Why R² of the multiple model is not directly comparable to R² of the per-season simple models
- Extrapolation and forecast uncertainty

### 3. Exact Tasks
**Part A — Evaluation**
1. For each simple model, predict its training years and calculate R², MAE, MSE and RMSE.
2. Build **Table A: Simple Regression Evaluation** (Season | R² | MAE | MSE | RMSE).
3. For the multiple model, predict all 19 rows and calculate R², MAE, MSE and RMSE.
4. Build **Table B: Multiple Regression Evaluation** (one row).
5. Also report the multiple model's MAE and RMSE broken down by season, so that errors can be compared with Table A on the same per-season basis.
6. Explain the R² difference: the multiple model's R² will be very high mainly because Season explains the large gap between hot and cool seasons, not because Year explains much. The simple models' R² measures only how well Year explains changes *within* one season. The two R² values answer different questions, so R² is not used to compare them.
7. Add the evaluation limitation note: metrics are calculated on the training data, so they describe fit, not true predictive accuracy. No overall score or ranking is created.

**Part B — 2030 Forecast**
8. Predict Year = 2030 with each of the four simple models.
9. Build four 2030 input rows for the multiple model (Year = 2030 with each season's dummy values), encoded exactly as in training, and predict.
10. Build the **final 2030 forecast table**: Season | Simple LR Forecast | Multiple LR Forecast | Latest Historical Average.
11. Briefly explain why the two forecasts differ: separate slopes vs one shared slope.
12. Add the forecast limitation note: a 4-year extrapolation from very few points is highly uncertain.
13. Add `evaluate_models` and `forecast_2030` functions to `model.py`, covering both approaches.

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 6 section)
- `model.py` (add `evaluate_models`, `forecast_2030`)

### 5. Input
- The four simple models (Day 4)
- The multiple model and encoding helper (Day 5)
- The seasonal modelling table (Day 2)

### 6. Output
- Table A: Simple regression evaluation
- Table B: Multiple regression evaluation, plus a per-season error breakdown
- The final 2030 forecast table with both forecasts
- Written interpretations and limitation notes

### 7. Code Work
- `r2_score`, `mean_absolute_error`, `mean_squared_error` from `sklearn.metrics`, with RMSE = √MSE
- `model.predict([[2030]])` for each simple model
- A small DataFrame of four 2030 rows, passed through the same encoding, then `predict` for the multiple model
- Assembling the result tables with pandas

### 8. Validation
- RMSE equals the square root of MSE everywhere.
- MAE ≤ RMSE everywhere (always true mathematically).
- In-sample R² values lie between 0 and 1.
- Exactly four forecasts per approach, only for 2030. No daily or monthly predictions.
- 2030 forecasts are within a sensible range (a few °C of historical values).
- Manual checks:
  - Simple: intercept + slope × 2030 equals `predict(2030)` for one season.
  - Multiple: intercept + β₁ × 2030 + (season dummy coefficient) equals the multiple forecast for one season.
- The 2030 input columns for the multiple model are in the same order as the training columns.

### 9. Expected Result
**Table A — Simple Linear Regression Evaluation**

| Season | R² | MAE | MSE | RMSE |
|---|---|---|---|---|
| Winter | … | … | … | … |
| Summer | … | … | … | … |
| Monsoon | … | … | … | … |
| Autumn | … | … | … | … |

**Table B — Multiple Linear Regression Evaluation**

| Model | R² | MAE | MSE | RMSE |
|---|---|---|---|---|
| Year + Season | … | … | … | … |

**2030 Forecast**

| Season | Simple LR (°C) | Multiple LR (°C) | Latest Historical (°C) |
|---|---|---|---|
| Winter | xx.xx | xx.xx | xx.xx |
| Summer | xx.xx | xx.xx | xx.xx |
| Monsoon | xx.xx | xx.xx | xx.xx |
| Autumn | xx.xx | xx.xx | xx.xx |

Some simple-model R² values may be low. That is a valid, honest result with this little data and should be explained, not hidden.

### 10. Stopping Point
Stop after all evaluation tables, the 2030 forecast table and their interpretations are complete.

---

## DAY 7 — Environmental Interpretation & Streamlit Application

### 1. Goal of the Day
Write the environmental interpretation, then build a simple Streamlit app that displays the project results.

### 2. Concepts We Will Learn
- Correlation vs causation
- Contextual (not causal) explanation of temperature trends
- Streamlit basics: `st.title`, `st.write`, `st.markdown`, `st.table`/`st.dataframe`, `st.pyplot`
- Reusing functions from `model.py` inside an app
- Caching data loading with `st.cache_data`

### 3. Exact Tasks
**Part A — Environmental interpretation (notebook)**
1. Write a short section (1–2 paragraphs) relating the observed seasonal trends to possible contextual factors: urbanization, deforestation, greenhouse-gas emissions, land-use change and energy demand.
2. Include a clear limitation statement: "Both regression approaches only show the statistical relationship between Year (and Season) and seasonal temperature. They do not prove that any of these factors caused the change."
3. Mention the short period (2022–2026) and small sample size.

**Part B — Streamlit app**
4. Create `app.py`, which imports functions from `model.py`.
5. Build the app sections in this order:
   1. Project title
   2. Location: Hyderabad, Telangana, India
   3. Historical period, with the data coverage note
   4. Seasonal statistics table
   5. Four seasonal trend graphs
   6. Regression model metrics: Table A (simple) and Table B (multiple), with the multiple model's coefficients
   7. 2030 forecast table (simple and multiple side by side)
   8. Environmental interpretation and limitations
6. Run the app locally with `streamlit run app.py`.

Features intentionally not included: login, database, API, live weather, city selector, maps, chatbot, filters, animations, deployment.

### 4. Files to Create/Modify
- `notebooks/temperature_analysis.ipynb` (Day 7 interpretation section)
- `app.py` (created)
- `model.py` (small adjustments only if the app needs them)

### 5. Input
- `data/hyderabad_weather.xlsx`
- `model.py` with all functions from Days 2–6
- The interpretation text

### 6. Output
- The environmental interpretation section in the notebook
- A working, single-page `app.py`

### 7. Code Work
- A short `app.py` that calls `model.py` functions in order: load → assign seasons → aggregate → statistics → train simple models → train multiple model → evaluate → forecast
- Displaying tables with `st.dataframe` or `st.table`
- Displaying matplotlib figures with `st.pyplot`
- Static markdown text for the interpretation

### 8. Validation
- The app starts without errors.
- All eight required sections appear in order.
- The numbers in the app exactly match the notebook (statistics, both evaluation tables, both forecasts).
- No extra features are present.
- The limitation statement is visible.

### 9. Expected Result
A clean, single-page app that scrolls from title to interpretation. Each section is simple enough to explain in one or two sentences during a viva.

### 10. Stopping Point
Stop when the app runs locally and matches the notebook results.

---

## DAY 8 — Testing, README, Report & PPT Preparation

### 1. Goal of the Day
Do a final end-to-end check, write the README, and prepare the report and PPT content for submission and viva.

### 2. Concepts We Will Learn
- Reproducibility (running everything from a clean start)
- Technical documentation
- Communicating statistical results and limitations
- Viva preparation: explaining simple vs multiple regression clearly

### 3. Exact Tasks
1. Restart the notebook kernel and run all cells from top to bottom.
2. Restart the Streamlit app and confirm that the results match the notebook.
3. Check the folder structure against the planned structure; remove any stray files.
4. Confirm that `requirements.txt` contains everything needed and nothing extra.
5. Write `README.md` with these sections:
   - Project title and objective
   - Location and dataset description (actual columns, date range)
   - Data verification summary
   - Season definitions and the Winter season-year convention
   - Methodology (seasonal aggregation → statistics → trends → 4 simple regressions → 1 multiple regression → evaluation → 2030 forecast)
   - Simple vs multiple regression explanation
   - Results summary (key tables)
   - Environmental interpretation and limitations
   - How to run (install requirements, open the notebook, run `streamlit run app.py`)
   - Project structure
6. Prepare the report outline: Abstract, Introduction, Dataset, Data Verification, Methodology, Descriptive Statistics, Trend Analysis, Simple Linear Regression, Multiple Linear Regression, Evaluation, 2030 Forecast, Environmental Interpretation, Limitations, Conclusion, References.
7. Prepare the PPT outline (about 14–16 slides), with the charts and tables to use on each slide.
8. Prepare a short list of likely viva questions with simple answers, including:
   - Why is this simple regression, and why is this multiple regression?
   - What is the dummy variable trap?
   - Why is Winter the baseline?
   - Why are the multiple model's fitted lines parallel?
   - Why is the multiple model's R² so high?
   - Why do the two 2030 forecasts differ?
   - Why no train/test split?
   - Does this prove urbanization causes warming?

### 4. Files to Create/Modify
- `README.md` (created)
- `notebooks/temperature_analysis.ipynb` (final re-run; small fixes only)
- `app.py` / `model.py` (small fixes only, if testing finds issues)
- Report and PPT content (prepared as outlines and text)

### 5. Input
- All project files from Days 1–7
- All tables and charts produced

### 6. Output
- A fully reproducible notebook
- A working Streamlit app
- A complete `README.md`
- Report outline and content
- PPT slide outline
- Viva question-and-answer notes

### 7. Code Work
- Minimal: only fixes found during end-to-end testing
- No new features

### 8. Validation
- "Restart & Run All" completes without errors.
- The app and the notebook show identical numbers.
- The README instructions work when followed step by step.
- Every project requirement is covered (checklist below).

### 9. Expected Result
A complete, submission-ready project that is easy to run, easy to read and easy to explain.

### 10. Stopping Point
The project is complete when the requirements checklist is fully ticked.

---

## Requirements Checklist (for Day 8)

| # | Requirement | Covered on |
|---|---|---|
| 1 | Historical temperature analysis | Days 1–3 |
| 2 | Seasonal grouping | Day 2 |
| 3 | Descriptive statistics | Day 3 |
| 4 | Seasonal trend visualization | Day 3 |
| 5a | Simple Linear Regression (4 models) | Day 4 |
| 5b | Multiple Linear Regression (Year + Season) | Day 5 |
| 6 | Model evaluation (R², MAE, MSE, RMSE) | Day 6 |
| 7 | 2030 forecasting | Day 6 |
| 8 | Environmental interpretation | Day 7 |
| 9 | Streamlit application | Day 7 |
| 10 | Documentation | Day 8 |
| 11 | PPT/report preparation | Day 8 |

---

## FINAL PROJECT FLOW

```
Dataset (Hyderabad daily weather, Dec 2021 – Sep 2026)
        ↓
Verification (missing, duplicates, dates, values, types, range)
        ↓
Season creation (Winter / Summer / Monsoon / Autumn)
        ↓
Seasonal averages (Year | Season | Average Temperature, 2022–2026)
        ↓
Statistics (mean, median, min, max, variance, std)
        ↓
Trend analysis (4 seasonal line charts)
        ↓
4 Simple Linear Regression models (X = Year)
        ↓
1 Multiple Linear Regression model (X = Year + Season)
        ↓
Model evaluation (R², MAE, MSE, RMSE)
        ↓
2030 forecast (Simple and Multiple, one value per season each)
        ↓
Environmental interpretation (with causation limitation)
        ↓
Streamlit
        ↓
Report + PPT
```

---

**Next step:** Say **"Start Day 1"** to begin implementation.
