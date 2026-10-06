"""Streamlit app: Seasonal Temperature Trend Analysis and 2030 Forecasting (Hyderabad).

Display layer only. Every number comes from the functions in model.py, the
same ones the notebook validates. Run with:  streamlit run app.py
"""

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

import model

DATA_PATH = Path(__file__).parent / "data" / "hyderabad_weather.xlsx"

# Theme colour name for each season (defined in .streamlit/config.toml)
SEASON_THEME = {"Winter": "blue", "Summer": "orange", "Monsoon": "green", "Autumn": "yellow"}
SEASON_MONTHS = {"Winter": "Dec – Feb", "Summer": "Mar – May", "Monsoon": "Jun – Sep", "Autumn": "Oct – Nov"}


@st.cache_data(show_spinner="Running the analysis…", max_entries=1)
def run_analysis(path):
    """Load → seasons → aggregate → statistics → models → evaluation → 2030 forecast."""
    daily = model.assign_season(model.load_data(path))
    seasonal = model.build_seasonal_table(daily)
    simple_models = model.train_simple_models(seasonal)
    multiple_model = model.train_multiple_model(seasonal)
    # Simple LR line from each season's first year to 2030, drawn under the actual points
    trend_years = pd.DataFrame({"Year": [seasonal["Year"].min(), model.FORECAST_YEAR]})
    trend = pd.concat(
        [trend_years.assign(Season=s, Trend=simple_models[s].predict(trend_years)) for s in model.SEASON_ORDER]
    )
    stats = model.seasonal_statistics(daily)
    forecast = model.forecast_2030(seasonal, simple_models, multiple_model)
    return {
        "first_day": daily["date"].min(),
        "last_day": daily["date"].max(),
        "n_days": len(daily),
        "seasonal": seasonal,
        "stats": stats,
        "slopes": model.simple_coefficients(simple_models, seasonal),
        "evaluation": model.evaluate_models(seasonal, simple_models, multiple_model),
        "coefficients": model.multiple_coefficients(multiple_model),
        "forecast": forecast,
        # Uses the same seasonal mean as the statistics table: one source of truth
        "increase": model.increase_from_mean(forecast, stats),
        "trend": trend,
    }


# Every season chart spans the same 6 °C (room for the 2030 point), so slopes compare across seasons
FORECAST_Y_SPAN = 6.0
LABEL_COLOR = "#5e4843"


def forecast_chart(seasonal, trend, forecast_row, season):
    """One season: actual yearly averages (solid), Simple LR trend (dashed) and the 2030 forecast (ring)."""
    data = seasonal.loc[seasonal["Season"] == season, ["Year", "Average_Temperature"]].sort_values("Year")
    line_data = trend[trend["Season"] == season]
    point_2030 = pd.DataFrame({"Year": [model.FORECAST_YEAR], "Forecast": [forecast_row["Simple LR (°C)"]]})
    color = model.SEASON_COLORS[season]
    # Label a point below the line when it is lower than both neighbours, so it stays off the line
    temps = data["Average_Temperature"].tolist()
    data["Below"] = [all(t < n for n in temps[max(i - 1, 0):i] + temps[i + 1:i + 2]) for i, t in enumerate(temps)]

    values = temps + line_data["Trend"].tolist() + point_2030["Forecast"].tolist()
    mid = (min(values) + max(values)) / 2
    years = sorted(seasonal["Year"].unique())
    x_scale = alt.Scale(domain=[years[0] - 0.4, model.FORECAST_YEAR + 0.6], nice=False)
    x_axis = alt.Axis(values=years + [model.FORECAST_YEAR], format="d", grid=False, labelColor=LABEL_COLOR)
    y_scale = alt.Scale(domain=[mid - FORECAST_Y_SPAN / 2, mid + FORECAST_Y_SPAN / 2], nice=False)
    x = alt.X("Year:Q", title=None, scale=x_scale, axis=x_axis)

    # Shaded forecast zone after the last historical year
    zone = alt.Chart(pd.DataFrame({"start": [years[-1] + 0.5], "end": [model.FORECAST_YEAR + 0.6]}))
    band = zone.mark_rect(color="#f8f1e7").encode(x=alt.X("start:Q", scale=x_scale, axis=x_axis, title=None), x2="end:Q")
    band_label = zone.mark_text(align="left", baseline="top", dx=6, dy=6, fontSize=10, color="#8a746f").encode(
        x="start:Q", y=alt.value(0), text=alt.value("FORECAST"))

    trend_line = alt.Chart(line_data).mark_line(color=color, strokeWidth=1.5, strokeDash=[5, 4], opacity=0.7).encode(
        x=x, y=alt.Y("Trend:Q", scale=y_scale))

    actual = alt.Chart(data).encode(
        x=x,
        y=alt.Y("Average_Temperature:Q", title="°C", scale=y_scale, axis=alt.Axis(labelColor=LABEL_COLOR)),
        tooltip=[alt.Tooltip("Year:Q", format="d"),
                 alt.Tooltip("Average_Temperature:Q", title="Actual average °C", format=".2f")],
    )
    line = actual.mark_line(color=color, strokeWidth=2.5)
    points = actual.mark_circle(color=color, size=70, opacity=1, stroke="white", strokeWidth=1.5)
    label = alt.Text("Average_Temperature:Q", format=".2f")
    above = actual.transform_filter("!datum.Below").mark_text(dy=-12, fontSize=11, color=LABEL_COLOR).encode(text=label)
    below = actual.transform_filter("datum.Below").mark_text(dy=15, fontSize=11, color=LABEL_COLOR).encode(text=label)

    predicted = alt.Chart(point_2030).encode(
        x=x, y=alt.Y("Forecast:Q", scale=y_scale),
        tooltip=[alt.Tooltip("Year:Q", format="d"),
                 alt.Tooltip("Forecast:Q", title="Simple LR forecast °C", format=".2f")],
    )
    ring = predicted.mark_point(shape="circle", size=150, filled=True, fill="white", stroke=color, strokeWidth=3,
                              opacity=1)
    ring_label = predicted.mark_text(dy=-16, fontSize=12, fontWeight="bold", color=color).encode(
        text=alt.Text("Forecast:Q", format=".2f"))

    return alt.layer(band, band_label, trend_line, line, points, above, below, ring, ring_label).properties(height=250)


# Sidebar navigation: project name + jump links to the section anchors on this page.
# The clicked item is highlighted in the theme's maroon; nothing is sent back to Python.
_SIDEBAR_NAV = st.components.v2.component(
    "sidebar_nav",
    html="""
<div class="brand">
  <div class="name"></div>
  <div class="place"><span class="icon">location_on</span><span class="place-text"></span></div>
</div>
<div class="label">Navigation</div>
<nav></nav>
""",
    css="""
:host { display: block; font-family: var(--st-font); color: var(--st-text-color); }
.brand { padding: 0 0.75rem 1.25rem; border-bottom: 1px solid var(--st-border-color); }
.name { font-family: var(--st-heading-font); font-size: 1.05rem; font-weight: 700; line-height: 1.35;
        color: var(--st-primary-color); }
.place { display: flex; align-items: center; gap: 0.3rem; margin-top: 0.5rem;
         font-size: 0.82rem; color: #8a746f; }
.place .icon { font-size: 1rem; }
.label { margin: 1.25rem 0 0.5rem; padding: 0 0.75rem; font-size: 0.7rem; font-weight: 600;
         letter-spacing: 0.08em; text-transform: uppercase; color: #8a746f; }
nav { display: flex; flex-direction: column; gap: 0.2rem; }
a { display: flex; align-items: center; gap: 0.7rem; padding: 0.55rem 0.75rem;
    border-radius: var(--st-base-radius); font-size: 0.92rem; font-weight: 500;
    color: #5e4843; text-decoration: none; transition: background 120ms, color 120ms; }
a .icon { font-size: 1.15rem; color: #8a746f; transition: color 120ms; }
a:hover { background: color-mix(in srgb, var(--st-primary-color) 6%, transparent); color: var(--st-primary-color); }
a:hover .icon { color: var(--st-primary-color); }
a.active { background: color-mix(in srgb, var(--st-primary-color) 11%, transparent);
           color: var(--st-primary-color); font-weight: 600; }
a.active .icon { color: var(--st-primary-color); }
a:focus-visible { outline: 2px solid var(--st-primary-color); outline-offset: 1px; }
.icon { font-family: "Material Symbols Rounded"; font-weight: normal; font-style: normal; line-height: 1;
        -webkit-font-feature-settings: "liga"; font-feature-settings: "liga"; }
""",
    js="""
const activeByRoot = new WeakMap()

export default function ({ data, parentElement }) {
  parentElement.querySelector(".name").textContent = data.name
  parentElement.querySelector(".place-text").textContent = data.place
  const nav = parentElement.querySelector("nav")
  const active = activeByRoot.get(parentElement) ?? data.sections[0].anchor

  nav.replaceChildren(...data.sections.map(({ label, anchor, icon }) => {
    const a = document.createElement("a")
    a.href = "#" + anchor
    a.className = anchor === active ? "active" : ""
    a.innerHTML = `<span class="icon">${icon}</span><span></span>`
    a.lastChild.textContent = label
    a.onclick = (e) => {
      e.preventDefault()
      activeByRoot.set(parentElement, anchor)
      nav.querySelectorAll("a").forEach((el) => el.classList.toggle("active", el === a))
      document.getElementById(anchor)?.scrollIntoView({ behavior: "smooth", block: "start" })
    }
    return a
  }))
}
""",
)


PROJECT_NAME = f"Seasonal Temperature Trend Analysis and {model.FORECAST_YEAR} Forecasting"

st.set_page_config(page_title="Hyderabad seasonal temperatures", page_icon=":material/thermostat:",
                   layout="wide", initial_sidebar_state=264)

results = run_analysis(DATA_PATH)
seasonal = results["seasonal"]
stats = results["stats"]
forecast = results["forecast"]

# ---------------------------------------------------------------------------
# Sidebar: project name and jump links to the sections below
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Overview", "overview", "home"),
    ("Seasonal Trends", "seasonal-trends", "show_chart"),
    ("Seasonal Statistics", "seasonal-statistics", "table_chart"),
    ("Model Results", "model-results", "functions"),
    (f"{model.FORECAST_YEAR} Forecast", "forecast-2030", "update"),
    ("Interpretation", "interpretation", "eco"),
]

with st.sidebar:
    _SIDEBAR_NAV(
        key="sidebar_nav",
        data={
            "name": PROJECT_NAME,
            "place": "Hyderabad, Telangana",
            "sections": [{"label": label, "anchor": anchor, "icon": icon} for label, anchor, icon in SECTIONS],
        },
    )

# ---------------------------------------------------------------------------
# Header: title, location and historical period (kept small)
# ---------------------------------------------------------------------------
st.title(f":red[{PROJECT_NAME}]", anchor="overview")
st.caption(
    f":material/location_on: Hyderabad, Telangana, India  ·  "
    f"Daily data {results['first_day']:%d %b %Y} – {results['last_day']:%d %b %Y} "
    f"({results['n_days']:,} days)  ·  Seasonal averages {seasonal['Year'].min()}–{seasonal['Year'].max()}"
)

# ---------------------------------------------------------------------------
# Seasonal trends and the 2030 forecast: one card per season
# ---------------------------------------------------------------------------
st.header(f":red[Seasonal trends and {model.FORECAST_YEAR} forecast]", anchor="seasonal-trends")
st.caption(
    f"Solid line: actual seasonal averages {seasonal['Year'].min()}–{seasonal['Year'].max()}  ·  "
    f"Dashed line: Simple Linear Regression trend  ·  Ring: {model.FORECAST_YEAR} predicted temperature.  "
    f"Every chart spans {FORECAST_Y_SPAN:.0f} °C, so the slopes can be compared across seasons."
)

for _, row in results["increase"].iterrows():
    season, color = row["Season"], SEASON_THEME[row["Season"]]
    predicted, mean, change = row["Simple LR (°C)"], row["Seasonal Mean (°C)"], row["Increase (°C)"]
    arrow = "↑" if change >= 0 else "↓"

    with st.container(border=True):
        st.markdown(f"#### :{color}[{season.upper()}] :gray[· {SEASON_MONTHS[season]}]")
        chart_col, figures_col = st.columns([2.3, 1], gap="medium", vertical_alignment="center")
        with chart_col:
            st.altair_chart(forecast_chart(seasonal, results["trend"], row, season))
        with figures_col:
            st.markdown(f":gray[{model.FORECAST_YEAR} Predicted Temperature]")
            st.markdown(f"## :{color}[{predicted:.2f} °C]")
            st.markdown(":gray[Increase from Avg Temperature]")
            st.markdown(f"### :red[{change:+.1f} °C {arrow}]")
            st.markdown(":gray[Avg Temperature (2022–2026)]")
            st.markdown(f"### {mean:.2f} °C")

# ---------------------------------------------------------------------------
# Seasonal statistics
# ---------------------------------------------------------------------------
st.header(":red[Seasonal statistics (2022–2026)]", anchor="seasonal-statistics")

stats_table = stats.reset_index()
stats_table.insert(1, "Months", stats_table["Season"].map(SEASON_MONTHS))
st.dataframe(
    stats_table,
    hide_index=True,
    column_config={
        "Mean": st.column_config.NumberColumn("Mean (°C)", format="%.2f"),
        "Median": st.column_config.NumberColumn("Median (°C)", format="%.2f"),
        "Minimum": st.column_config.NumberColumn("Min (°C)", format="%.2f"),
        "Maximum": st.column_config.NumberColumn("Max (°C)", format="%.2f"),
        "Variance": st.column_config.NumberColumn("Variance", format="%.2f"),
        "Std_Dev": st.column_config.NumberColumn("Std dev", format="%.2f"),
    },
)

# ---------------------------------------------------------------------------
# Regression models
# ---------------------------------------------------------------------------
st.header(":red[Regression models]", anchor="model-results")

st.subheader("Simple linear regression")
st.caption("Four models, one per season: Year → seasonal average temperature.")
simple_table = results["slopes"][["Season", "Slope (°C/year)"]].merge(results["evaluation"]["simple"], on="Season")
metric_format = {m: st.column_config.NumberColumn(m, format="%.3f") for m in ["R²", "MAE", "MSE", "RMSE"]}
st.dataframe(
    simple_table,
    hide_index=True,
    column_config={"Slope (°C/year)": st.column_config.NumberColumn("Trend (°C/year)", format="%+.3f"),
                   **metric_format},
)

st.subheader("Multiple linear regression")
coefs = results["coefficients"].set_index("Feature")["Coefficient"]
st.caption(
    f"One model on all {len(seasonal)} points: Year + Season → temperature. "
    f"Shared trend **{coefs['Year']:+.3f} °C/year**; compared with Winter, "
    f"Summer is {coefs['Season_Summer']:+.2f} °C, Monsoon {coefs['Season_Monsoon']:+.2f} °C "
    f"and Autumn {coefs['Season_Autumn']:+.2f} °C."
)
st.dataframe(results["evaluation"]["multiple"], hide_index=True, column_config=metric_format)
st.info(
    "The two R² values are not comparable: the multiple model's high R² comes mainly from Season "
    "(the gap between hot and cool seasons), not from Year.",
    icon=":material/info:",
)

st.subheader(f"{model.FORECAST_YEAR} forecast: Simple vs Multiple linear regression", anchor="forecast-2030")
st.caption("The season cards above use Simple LR; the Multiple LR forecast is shown here for comparison.")
st.dataframe(
    forecast[["Season", "Simple LR (°C)", "Multiple LR (°C)"]],
    hide_index=True,
    column_config={
        "Simple LR (°C)": st.column_config.NumberColumn(f"Simple LR {model.FORECAST_YEAR} (°C)", format="%.2f"),
        "Multiple LR (°C)": st.column_config.NumberColumn(f"Multiple LR {model.FORECAST_YEAR} (°C)", format="%.2f"),
    },
)


# ---------------------------------------------------------------------------
# Environmental interpretation and limitations
# ---------------------------------------------------------------------------
st.header(":red[Environmental interpretation and limitations]", anchor="interpretation")
increase = results["increase"].set_index("Season")["Increase (°C)"]

with st.container(border=True):
    st.markdown("#### :red[:material/thermostat: What the model predicts]")
    st.markdown(
        f"**Every season is expected to be warmer by {model.FORECAST_YEAR}** than its 2022–2026 average. "
        f"The largest rise is in **:{SEASON_THEME[increase.idxmax()]}[{increase.idxmax()}] "
        f"({increase.max():+.1f} °C)** and the smallest in "
        f"**:{SEASON_THEME[increase.idxmin()]}[{increase.idxmin()}] ({increase.min():+.1f} °C)**."
    )
    for col, (season, change) in zip(st.columns(len(increase)), increase.items()):
        with col:
            st.markdown(f":{SEASON_THEME[season]}-badge[{season.upper()}]")
            st.markdown(f"### :{SEASON_THEME[season]}[{change:+.1f} °C ↑]")

with st.container(border=True):
    st.markdown("#### :red[:material/eco: Possible contributing factors]")
    st.markdown("Warming in a fast-growing city like Hyderabad may be influenced by:")
    factors = [
        ("location_city", "Urbanisation and heat islands",
         "Concrete and asphalt absorb heat by day and release it at night"),
        ("park", "Loss of green cover", "Fewer trees and lakes means less shade and less cooling"),
        ("landscape", "Land-use change", "Open and agricultural land turned into built surfaces"),
        ("bolt", "Rising energy use", "More cooling demand releases more waste heat"),
        ("factory", "Greenhouse-gas emissions", "Global warming raises the baseline everywhere"),
        ("dns", "Data centers and infrastructure", "Growth of energy-intensive facilities"),
    ]
    factor_cols = st.columns(2, gap="medium")
    for i, (icon, title, detail) in enumerate(factors):
        with factor_cols[i % 2]:
            st.markdown(f":red[:material/{icon}:] **{title}**  \n:gray[{detail}]")
st.warning(
    "**The regression shows a trend over time, not its cause.** "
    "It does not prove that any of these factors caused the increase. Each trend comes from only 4–5 points "
    f"per season (2022–2026), and the {model.FORECAST_YEAR} forecasts extend it 4 years beyond the data, "
    "so they are highly uncertain.",
    icon=":material/warning:",
)

st.divider()
st.caption("Data: Hyderabad daily weather (temperature_2m_mean)  ·  Method: scikit-learn LinearRegression")
