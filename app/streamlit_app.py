"""Streamlit dashboard for the Fabrication Data Platform demo."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import streamlit as st

from app import utils


st.set_page_config(
    page_title="Fabrication Data Platform Demo",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_data():
    """Load all warehouse artifacts needed for the dashboard."""
    jobs = utils.load_jobs_integrated()
    features = utils.load_feature_table()
    quality = utils.load_quality_report()
    return jobs, features, quality


def render_system_overview():
    """Render the system overview tab with diagram and narrative."""
    st.subheader("How Data Flows Across the Fabrication Platform")
    image_path = Path(__file__).resolve().parent / "assets" / "system_diagram.png"
    if image_path.exists():
        st.image(str(image_path), use_column_width=True)
    else:
        st.warning("System diagram not found. Add app/assets/system_diagram.png to display it.")

    st.markdown(
        """
        Monumental's fabrication data pipeline stitches together CAM programming,
        robotic execution, quality measurements, and ERP context. ETL jobs convert these
        siloed feeds into a warehouse, enabling shared features for downstream analytics.
        """
    )


def render_kpis(jobs, features):
    """Render key performance indicators."""
    st.subheader("Production Pulse")
    col1, col2, col3, col4 = st.columns(4)
    avg_minutes = jobs["duration_s"].mean() / 60
    col1.metric("Avg Carve Time (min)", f"{avg_minutes:0.1f}")
    col2.metric("Total Jobs", f"{jobs['job_id'].nunique()}")
    col3.metric("Avg Surface Score", f"{jobs['surface_score'].mean():0.1f} / 100")
    col4.metric("Avg Profit Margin", f"{features['profit_margin'].mean():0.1%}")


def render_process_analytics(features):
    """Render process analytics visuals."""
    st.subheader("Process Analytics")
    scatter1, scatter2 = st.columns(2)

    scatter1.plotly_chart(
        px.scatter(
            features,
            x="complexity_per_cm3",
            y="duration_s",
            color="material",
            size="volume_removed_cm3",
            hover_name="job_id",
            labels={
                "complexity_per_cm3": "Toolpath Complexity per cm³",
                "duration_s": "Duration (s)",
            },
            title="Complexity vs. Carve Time",
        ),
        use_container_width=True,
    )

    hardness_df = features.copy()
    hardness_df["stone_hardness"] = hardness_df["stone_type"].fillna("").map(utils.stone_hardness_scale)

    scatter2.plotly_chart(
        px.scatter(
            hardness_df,
            x="stone_hardness",
            y="energy_per_cm3",
            color="stone_type",
            hover_name="job_id",
            labels={
                "stone_hardness": "Approx. Mohs Hardness",
                "energy_per_cm3": "Energy per cm³ (kWh)",
            },
            title="Energy Load vs. Stone Hardness",
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        px.density_heatmap(
            features,
            x="feed_rate_mm_min",
            y="surface_score",
            marginal_x="histogram",
            marginal_y="histogram",
            nbinsx=30,
            nbinsy=20,
            labels={
                "feed_rate_mm_min": "Feed Rate (mm/min)",
                "surface_score": "Surface Quality Score",
            },
            title="Surface Quality vs. Feed Rate",
        ),
        use_container_width=True,
    )


def render_cost_profitability(jobs, features):
    """Render cost and profitability insights."""
    st.subheader("Cost & Profitability")
    joined = features.merge(
        jobs[["job_id", "defect_count"]], on="job_id", how="left", suffixes=("", "_jobs")
    )
    joined["profit_usd"] = joined["revenue_usd"] - joined["tool_wear_cost_usd"]

    st.dataframe(
        joined[
            [
                "job_id",
                "material",
                "stone_type",
                "labor_hours",
                "tool_wear_cost_usd",
                "revenue_usd",
                "profit_usd",
                "defect_count",
            ]
        ].set_index("job_id"),
        use_container_width=True,
        height=350,
    )

    st.plotly_chart(
        px.bar(
            joined,
            x="stone_type",
            y="profit_usd",
            color="stone_type",
            title="Profit by Stone Type",
            labels={"stone_type": "Stone Type", "profit_usd": "Profit (USD)"},
        ),
        use_container_width=True,
    )


def render_feature_store(features):
    """Render engineered feature list and correlations."""
    st.subheader("ML Feature Store Overview")
    feature_columns = [
        col
        for col in features.columns
        if col
        not in {
            "job_id",
            "material",
            "stone_type",
            "path_length_mm",
            "volume_removed_cm3",
            "spindle_current_a",
            "duration_s",
            "surface_score",
            "tool_wear_cost_usd",
            "labor_hours",
            "revenue_usd",
        }
    ]

    st.write("Engineered features available to downstream consumers:")
    st.markdown(
        "\n".join(f"- `{column}`" for column in feature_columns),
        unsafe_allow_html=False,
    )

    numeric_cols = feature_columns + ["duration_s"]
    corr = features[numeric_cols].corr()
    st.plotly_chart(
        px.imshow(
            corr,
            zmin=-1,
            zmax=1,
            color_continuous_scale="RdBu",
            title="Feature Correlation with Duration",
        ),
        use_container_width=True,
    )


def render_data_quality(quality_report):
    """Render data quality metrics as progress and status."""
    st.subheader("Data Quality Monitoring")
    completeness = quality_report["completeness_percent"]
    for source, pct in completeness.items():
        st.progress(min(int(pct), 100), text=f"{source.title()} completeness: {pct}%")

    col1, col2 = st.columns(2)
    critical_nulls = quality_report["critical_nulls"]
    col1.metric("Null duration_s entries", critical_nulls.get("duration_s", 0))
    col2.metric("Null revenue_usd entries", critical_nulls.get("revenue_usd", 0))

    outliers = quality_report["carve_time_outliers"]
    st.info(
        f"Carve time outliers detected: {outliers['count']} "
        f"(job IDs: {', '.join(outliers['job_ids']) if outliers['job_ids'] else 'none'})"
    )

    tool_validations = quality_report["tool_catalog_validation"]
    st.info(
        f"Invalid tool IDs: {tool_validations['invalid_count']} "
        f"({', '.join(tool_validations['unknown_ids']) if tool_validations['unknown_ids'] else 'none'})"
    )


def main():
    """Application entry point."""
    st.title("Fabrication Data Platform Demo")
    try:
        jobs, features, quality = load_data()
    except FileNotFoundError as exc:
        st.error(
            f"{exc}\\n\\nRun the data generation + ETL scripts before launching the dashboard."
        )
        return

    tabs = st.tabs(
        [
            "System Overview",
            "KPIs",
            "Process Analytics",
            "Cost & Profitability",
            "ML Feature Store",
            "Data Quality",
        ]
    )

    with tabs[0]:
        render_system_overview()
    with tabs[1]:
        render_kpis(jobs, features)
    with tabs[2]:
        render_process_analytics(features)
    with tabs[3]:
        render_cost_profitability(jobs, features)
    with tabs[4]:
        render_feature_store(features)
    with tabs[5]:
        render_data_quality(quality)

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color: #666;'>"
        "Synthetic data • Python ETL (DuckDB + Pandas) • KUKA handles robot monitoring; "
        "this focuses on fabrication performance"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
