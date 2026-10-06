"""Reusable functions for the Hyderabad seasonal temperature project.

The notebook explains each step; this module holds the same logic so that
the Streamlit app can reuse it.
"""

import pandas as pd

# Seasons in the order they are shown everywhere in the project
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Autumn"]

# Month number -> season
MONTH_TO_SEASON = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Autumn", 11: "Autumn",
}

# The modelling table starts at 2022 (2021 has only 2 days, which belong to Winter 2022)
FIRST_SEASON_YEAR = 2022


def load_data(path):
    """Load the daily dataset and keep only the columns used in the analysis."""
    df = pd.read_excel(path, engine="openpyxl")
    return df[["date", "temperature_2m_mean"]].copy()


def assign_season(df):
    """Add Month, Season and Season_Year columns.

    December belongs to the next year's winter (meteorological convention),
    e.g. Dec 2021 + Jan 2022 + Feb 2022 = Winter 2022.
    """
    df = df.copy()
    df["Month"] = df["date"].dt.month
    df["Season"] = df["Month"].map(MONTH_TO_SEASON)
    df["Season_Year"] = df["date"].dt.year
    df.loc[df["Month"] == 12, "Season_Year"] += 1
    return df


def season_day_counts(df):
    """Number of days in each (Season_Year, Season) group."""
    counts = df.groupby(["Season_Year", "Season"]).size().reset_index(name="Days")
    counts["Season"] = pd.Categorical(counts["Season"], categories=SEASON_ORDER, ordered=True)
    return counts.sort_values(["Season_Year", "Season"]).reset_index(drop=True)


def build_seasonal_table(df):
    """Build the modelling table: Year | Season | Average_Temperature.

    Only season-years from 2022 onwards are kept. Seasons that do not exist in
    the data (Autumn 2026) produce no row. Monsoon 2026 is partial (data ends
    on 26 Sep 2026) and is kept.
    """
    df = df[df["Season_Year"] >= FIRST_SEASON_YEAR]
    table = (
        df.groupby(["Season_Year", "Season"])["temperature_2m_mean"]
        .mean()
        .reset_index()
        .rename(columns={"Season_Year": "Year", "temperature_2m_mean": "Average_Temperature"})
    )
    table["Season"] = pd.Categorical(table["Season"], categories=SEASON_ORDER, ordered=True)
    return table.sort_values(["Year", "Season"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Day 3: descriptive statistics and trend plots
# ---------------------------------------------------------------------------

# One fixed colour per season, used in every chart
SEASON_COLORS = {
    "Winter": "#2a78d6",
    "Summer": "#eb6834",
    "Monsoon": "#1baf7a",
    "Autumn": "#eda100",
}

# Every trend chart shows the same temperature span, so slopes look comparable
TREND_Y_SPAN = 5.0


def seasonal_statistics(df):
    """Mean, median, min, max, variance and std of daily temperature per season.

    Uses the daily values (not the seasonal averages) over the full period.
    Variance and standard deviation are sample values (ddof=1, the pandas default).
    """
    stats = (
        df.groupby("Season")["temperature_2m_mean"]
        .agg(["mean", "median", "min", "max", "var", "std"])
        .reindex(SEASON_ORDER)
    )
    stats.columns = ["Mean", "Median", "Minimum", "Maximum", "Variance", "Std_Dev"]
    stats.index.name = "Season"
    return stats.round(2)


def yearly_seasonal_pivot(seasonal):
    """Years x Seasons table of average temperatures."""
    pivot = seasonal.pivot(index="Year", columns="Season", values="Average_Temperature")
    return pivot[SEASON_ORDER].round(2)


def _style_axis(ax):
    """Light, recessive grid and axes."""
    ax.grid(axis="y", color="#e4e3df", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#b5b4ad")
    ax.tick_params(colors="#52514e")


def plot_season_trend(seasonal, season, ax=None):
    """Line chart of one season's average temperature by year."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    data = seasonal[seasonal["Season"] == season].sort_values("Year")
    years, temps = data["Year"], data["Average_Temperature"]

    ax.plot(years, temps, color=SEASON_COLORS[season], linewidth=2,
            marker="o", markersize=8, markeredgecolor="white", markeredgewidth=1.5)
    values = list(temps)
    for i, (x, y) in enumerate(zip(years, values)):
        # Label below a point that is lower than its neighbours, so it stays off the line
        neighbours = values[max(i - 1, 0):i] + values[i + 1:i + 2]
        below = all(y < n for n in neighbours)
        ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points",
                    xytext=(0, -15 if below else 9), ha="center", fontsize=9, color="#52514e")

    mid = (temps.min() + temps.max()) / 2
    ax.set_ylim(mid - TREND_Y_SPAN / 2, mid + TREND_Y_SPAN / 2)
    ax.set_xticks(list(years))                       # whole years only
    ax.set_xlim(years.min() - 0.4, years.max() + 0.4)
    ax.set_title(f"{season}: average temperature by year", loc="left", fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel("Average seasonal temperature (°C)")
    _style_axis(ax)
    return ax


def plot_all_trends(seasonal):
    """The four seasonal trend charts in a 2 x 2 figure."""
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, season in zip(axes.flat, SEASON_ORDER):
        plot_season_trend(seasonal, season, ax=ax)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Day 4: Simple Linear Regression (one model per season, X = Year)
# ---------------------------------------------------------------------------

def train_simple_models(seasonal):
    """Fit one LinearRegression per season: Year -> Average_Temperature.

    Returns a dict {season: fitted model}. Each model sees only its own
    season's rows (5 points, or 4 for Autumn).
    """
    from sklearn.linear_model import LinearRegression

    models = {}
    for season in SEASON_ORDER:
        data = seasonal[seasonal["Season"] == season]
        X = data[["Year"]]                      # 2-D: (n_samples, 1 feature)
        y = data["Average_Temperature"]
        models[season] = LinearRegression().fit(X, y)
    return models


def simple_coefficients(models, seasonal):
    """Table of Season | Points | Slope | Intercept | Equation."""
    rows = []
    for season, m in models.items():
        slope, intercept = m.coef_[0], m.intercept_
        rows.append({
            "Season": season,
            "Points": int((seasonal["Season"] == season).sum()),
            "Slope (°C/year)": round(slope, 4),
            "Intercept": round(intercept, 2),
            "Equation": f"Temp = {intercept:.2f} {'+' if slope >= 0 else '-'} {abs(slope):.4f} × Year",
        })
    return pd.DataFrame(rows)


def plot_simple_fit(seasonal, season, model, ax=None):
    """Actual seasonal averages (points) with the fitted simple regression line."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(6, 4))
    data = seasonal[seasonal["Season"] == season].sort_values("Year")
    color = SEASON_COLORS[season]

    ax.plot(data["Year"], model.predict(data[["Year"]]), color=color, linewidth=2,
            label="Fitted line")
    ax.scatter(data["Year"], data["Average_Temperature"], s=64, color=color,
               edgecolor="white", linewidth=1.5, zorder=3, label="Actual average")

    mid = (data["Average_Temperature"].min() + data["Average_Temperature"].max()) / 2
    ax.set_ylim(mid - TREND_Y_SPAN / 2, mid + TREND_Y_SPAN / 2)
    ax.set_xticks(list(data["Year"]))
    ax.set_xlim(data["Year"].min() - 0.4, data["Year"].max() + 0.4)
    slope = model.coef_[0]
    ax.set_title(f"{season}: actual vs fitted (slope {slope:+.3f} °C/year)", loc="left", fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel("Average seasonal temperature (°C)")
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    _style_axis(ax)
    return ax


# ---------------------------------------------------------------------------
# Day 5: Multiple Linear Regression (one model for all seasons, X = Year + Season)
# ---------------------------------------------------------------------------

# Winter is the baseline, so it has no column of its own
MULTIPLE_FEATURES = ["Year", "Season_Summer", "Season_Monsoon", "Season_Autumn"]


def encode_features(data):
    """Year plus one-hot Season columns (Winter dropped as the baseline).

    Season is made an ordered categorical first, so drop_first always drops
    Winter, and even a single row (e.g. Summer 2030) gets all three columns.
    """
    data = data[["Year", "Season"]].copy()
    data["Season"] = pd.Categorical(data["Season"], categories=SEASON_ORDER, ordered=True)
    X = pd.get_dummies(data, columns=["Season"], drop_first=True, dtype=int)
    return X[MULTIPLE_FEATURES]


def train_multiple_model(seasonal):
    """Fit one LinearRegression on all rows: Year + Season -> Average_Temperature."""
    from sklearn.linear_model import LinearRegression

    X = encode_features(seasonal)
    y = seasonal["Average_Temperature"]
    return LinearRegression().fit(X, y)


def multiple_coefficients(model):
    """Table of Feature | Coefficient, with the intercept as the first row."""
    rows = [{"Feature": "Intercept", "Coefficient": round(model.intercept_, 4)}]
    for feature, coef in zip(model.feature_names_in_, model.coef_):
        rows.append({"Feature": feature, "Coefficient": round(coef, 4)})
    return pd.DataFrame(rows)


def plot_multiple_fit(seasonal, model, ax=None):
    """Actual seasonal averages with the four parallel lines of the multiple model."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(9, 5.5))
    years = sorted(seasonal["Year"].unique())
    for season in SEASON_ORDER:
        color = SEASON_COLORS[season]
        data = seasonal[seasonal["Season"] == season].sort_values("Year")
        # Each line covers only its own season's years (Autumn stops at 2025)
        fitted = model.predict(encode_features(data))
        ax.plot(data["Year"], fitted, color=color, linewidth=2)
        ax.scatter(data["Year"], data["Average_Temperature"], s=64, color=color,
                   edgecolor="white", linewidth=1.5, zorder=3)
        # Name each line at its right end instead of using a legend
        ax.annotate(season, (data["Year"].iloc[-1], fitted[-1]), textcoords="offset points",
                    xytext=(8, 0), va="center", fontsize=10, color=color)

    ax.set_xticks(years)
    ax.set_xlim(years[0] - 0.4, years[-1] + 0.9)
    year_coef = model.coef_[list(model.feature_names_in_).index("Year")]
    ax.set_title(f"Multiple regression: one shared slope ({year_coef:+.3f} °C/year), "
                 "one level per season", loc="left", fontsize=11)
    ax.set_xlabel("Year")
    ax.set_ylabel("Average seasonal temperature (°C)")
    _style_axis(ax)
    return ax


# ---------------------------------------------------------------------------
# Day 6: evaluation (R², MAE, MSE, RMSE) and the 2030 forecast
# ---------------------------------------------------------------------------

FORECAST_YEAR = 2030


def regression_metrics(actual, predicted):
    """R², MAE, MSE and RMSE (= √MSE) for one set of predictions."""
    import numpy as np
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    mse = mean_squared_error(actual, predicted)
    return {
        "R²": r2_score(actual, predicted),
        "MAE": mean_absolute_error(actual, predicted),
        "MSE": mse,
        "RMSE": np.sqrt(mse),
    }


def _predict_both(seasonal, simple_models, multiple_model):
    """Seasonal table with Simple and Multiple predictions for every historical row."""
    data = seasonal.copy()
    data["Pred_Simple"] = 0.0
    for season, m in simple_models.items():
        mask = data["Season"] == season
        data.loc[mask, "Pred_Simple"] = m.predict(data.loc[mask, ["Year"]])
    data["Pred_Multiple"] = multiple_model.predict(encode_features(data))
    return data


def evaluate_models(seasonal, simple_models, multiple_model):
    """In-sample evaluation of both approaches.

    Returns a dict of three tables:
    - "simple":    Season | R² | MAE | MSE | RMSE   (one row per simple model)
    - "multiple":  Model  | R² | MAE | MSE | RMSE   (one row, all 19 points)
    - "by_season": the multiple model's MAE, MSE and RMSE per season, next to the simple ones
    """
    data = _predict_both(seasonal, simple_models, multiple_model)

    simple_rows, season_rows = [], []
    for season in SEASON_ORDER:
        d = data[data["Season"] == season]
        simple_m = regression_metrics(d["Average_Temperature"], d["Pred_Simple"])
        multi_m = regression_metrics(d["Average_Temperature"], d["Pred_Multiple"])
        simple_rows.append({"Season": season, **simple_m})
        season_rows.append({
            "Season": season,
            "MAE (Simple)": simple_m["MAE"], "MAE (Multiple)": multi_m["MAE"],
            "MSE (Simple)": simple_m["MSE"], "MSE (Multiple)": multi_m["MSE"],
            "RMSE (Simple)": simple_m["RMSE"], "RMSE (Multiple)": multi_m["RMSE"],
        })

    multiple = pd.DataFrame([{
        "Model": "Year + Season",
        **regression_metrics(data["Average_Temperature"], data["Pred_Multiple"]),
    }])
    # Full precision; round only when displaying
    return {
        "simple": pd.DataFrame(simple_rows),
        "multiple": multiple,
        "by_season": pd.DataFrame(season_rows),
    }


def forecast_2030(seasonal, simple_models, multiple_model, year=FORECAST_YEAR):
    """Forecast table: Season | Simple LR | Multiple LR | latest historical average.

    The multiple model's input rows go through encode_features, so they are
    encoded exactly as in training.
    """
    future = pd.DataFrame({"Year": year, "Season": SEASON_ORDER})
    multi_pred = multiple_model.predict(encode_features(future))

    rows = []
    for season, multi in zip(SEASON_ORDER, multi_pred):
        latest = seasonal[seasonal["Season"] == season].sort_values("Year").iloc[-1]
        rows.append({
            "Season": season,
            "Simple LR (°C)": simple_models[season].predict(pd.DataFrame({"Year": [year]}))[0],
            "Multiple LR (°C)": multi,
            "Latest Historical (°C)": latest["Average_Temperature"],
            "Latest Year": int(latest["Year"]),
        })
    return pd.DataFrame(rows)   # full precision; round only when displaying


def increase_from_mean(forecast, stats):
    """2030 Simple LR forecast vs the 2022–2026 seasonal mean from seasonal_statistics.

    The mean is taken straight from the statistics table, so both show the same value.
    The forecast is rounded to 2 decimals (as displayed) so the increase matches what the reader sees.
    """
    table = forecast[["Season", "Simple LR (°C)"]].copy()
    table["Seasonal Mean (°C)"] = table["Season"].map(stats["Mean"])
    table["Increase (°C)"] = table["Simple LR (°C)"].round(2) - table["Seasonal Mean (°C)"]
    return table
