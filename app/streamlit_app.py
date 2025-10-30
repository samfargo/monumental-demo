"""Streamlit dashboard for the Fabrication Data Platform demo."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import plotly.express as px
import streamlit as st

import utils


st.set_page_config(
    page_title="Fabrication Data Platform Demo",
    layout="wide",
)


def configure_visual_defaults() -> None:
    """Set global theming defaults for charts and layout."""
    px.defaults.template = "plotly_white"
    px.defaults.color_discrete_sequence = [
        "#2563EB",
        "#6366F1",
        "#0EA5E9",
        "#14B8A6",
        "#F97316",
        "#FACC15",
    ]


def inject_custom_css() -> None:
    """Inject a refined visual design system for the dashboard."""
    st.markdown(
        dedent(
            """
            <style>
                :root {
                    --primary: #2563EB;
                    --primary-accent: #1D4ED8;
                    --hero-gradient-start: #0F172A;
                    --hero-gradient-end: rgba(37, 99, 235, 0.55);
                    --surface: #0B1120;
                    --surface-elevated: #0F172A;
                    --surface-light: #F8FAFC;
                    --text-strong: #0F172A;
                    --text-muted: #64748B;
                    --metric-glass: rgba(15, 23, 42, 0.55);
                }

                .stApp {
                    background: linear-gradient(165deg, var(--surface) 0%, rgba(15, 23, 42, 0.92) 38%, var(--surface-light) 100%);
                }

                .main .block-container {
                    padding-top: 1.2rem;
                    padding-bottom: 3rem;
                    max-width: 1180px;
                }

                .hero-card {
                    background: linear-gradient(135deg, var(--hero-gradient-start) 0%, rgba(15, 23, 42, 0.92) 45%, var(--hero-gradient-end) 100%);
                    border-radius: 22px;
                    padding: 2.6rem 2.8rem 2.4rem;
                    position: relative;
                    overflow: hidden;
                    box-shadow: 0 30px 70px rgba(15, 23, 42, 0.35);
                    color: #E2E8F0;
                }

                .hero-card::after {
                    content: "";
                    position: absolute;
                    top: -120px;
                    right: -80px;
                    width: 320px;
                    height: 320px;
                    background: radial-gradient(circle, rgba(59,130,246,0.5) 0%, rgba(15, 23, 42, 0) 70%);
                    opacity: 0.9;
                }

                .hero-heading {
                    font-size: 2.3rem;
                    font-weight: 700;
                    margin-bottom: 0.75rem;
                    letter-spacing: 0.01em;
                }

                .hero-subtitle {
                    font-size: 1.05rem;
                    max-width: 560px;
                    line-height: 1.6;
                    color: rgba(226, 232, 240, 0.86);
                }

                .hero-badges {
                    display: flex;
                    gap: 0.75rem;
                    flex-wrap: wrap;
                    margin-top: 1.6rem;
                }

                .hero-badge {
                    background: rgba(226, 232, 240, 0.12);
                    border-radius: 999px;
                    padding: 0.45rem 1.1rem;
                    font-size: 0.85rem;
                    letter-spacing: 0.04em;
                    text-transform: uppercase;
                    border: 1px solid rgba(148, 163, 184, 0.2);
                }

                .metric-card {
                    position: relative;
                    background: var(--metric-glass);
                    padding: 1.4rem 1.6rem;
                    border-radius: 18px;
                    border: 1px solid rgba(148, 163, 184, 0.18);
                    box-shadow: 0 24px 48px rgba(15, 23, 42, 0.3);
                    backdrop-filter: blur(14px);
                    color: #E2E8F0;
                    min-height: 160px;
                }

                .metric-card__icon {
                    font-size: 1.8rem;
                    margin-bottom: 1.1rem;
                    line-height: 1;
                }

                .metric-card__value {
                    font-size: 2.1rem;
                    font-weight: 700;
                    letter-spacing: 0.01em;
                    margin-bottom: 0.35rem;
                    color: #F8FAFC;
                }

                .metric-card__label {
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    font-size: 0.78rem;
                    color: rgba(226, 232, 240, 0.72);
                }

                .metric-card__caption {
                    margin-top: 0.6rem;
                    font-size: 0.82rem;
                    color: rgba(226, 232, 240, 0.6);
                }

               .metric-card::after {
                    content: "";
                    position: absolute;
                    inset: 1px;
                    border-radius: 17px;
                    pointer-events: none;
                    background: linear-gradient(135deg, rgba(37, 99, 235, 0.32) 0%, rgba(14, 165, 233, 0.08) 65%);
                    opacity: 0.55;
                }

                .metric-card > * {
                    position: relative;
                    z-index: 2;
                }

                .metric-card::before {
                    content: "";
                    position: absolute;
                    inset: 0;
                    border-radius: 18px;
                    background: linear-gradient(145deg, rgba(15, 23, 42, 0.75), rgba(37, 99, 235, 0.22));
                    z-index: 1;
                }

                .metric-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1.25rem;
                    width: 100%;
                }

                button[data-baseweb="tab"] {
                    border: none;
                    padding: 0.85rem 1.4rem;
                    font-weight: 600;
                    font-size: 0.95rem;
                    color: var(--text-muted);
                    background-color: transparent;
                }

                button[data-baseweb="tab"][aria-selected="true"] {
                    color: var(--primary);
                    background: rgba(37, 99, 235, 0.12);
                    border-radius: 12px 12px 0 0;
                    border-bottom: 2px solid var(--primary);
                }

                button[data-baseweb="tab"]:focus {
                    outline: none;
                    box-shadow: none;
                }

                h2, .stSubheader {
                    color: var(--text-strong);
                }

                [data-testid="stDataFrame"] {
                    background: rgba(15, 23, 42, 0.03);
                    border-radius: 16px;
                    border: 1px solid rgba(148, 163, 184, 0.18);
                    box-shadow: inset 0 1px 0 rgba(148, 163, 184, 0.08);
                    padding: 0.6rem;
                }

                .quality-progress {
                    display: flex;
                    flex-direction: column;
                    gap: 0.75rem;
                    margin-top: 1rem;
                }

                .quality-progress__row {
                    display: flex;
                    align-items: center;
                    gap: 0.85rem;
                }

                .quality-progress__label {
                    min-width: 160px;
                    font-weight: 600;
                    font-size: 0.9rem;
                    color: var(--text-strong);
                    text-transform: capitalize;
                }

                .quality-progress__bar {
                    flex-grow: 1;
                    height: 10px;
                    background: rgba(148, 163, 184, 0.25);
                    border-radius: 999px;
                    overflow: hidden;
                    position: relative;
                }

                .quality-progress__fill {
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    background: linear-gradient(90deg, var(--primary) 0%, #38BDF8 100%);
                    border-radius: 999px;
                }

                .quality-progress__value {
                    min-width: 58px;
                    text-align: right;
                    font-weight: 600;
                    color: var(--text-muted);
                }

                .stAlert {
                    border-radius: 16px;
                    border-left: 4px solid var(--primary);
                    background: rgba(37, 99, 235, 0.08);
                }

                .stAlert p {
                    color: var(--text-strong) !important;
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_metric_card(title: str, value: str, icon: str, caption: str | None = None) -> str:
    """Return HTML for a stylized KPI card."""
    caption_html = (
        f"<div class='metric-card__caption'>{caption}</div>" if caption else ""
    )
    return dedent(
        f"""
        <div class="metric-card">
            <div class="metric-card__icon">{icon}</div>
            <div class="metric-card__value">{value}</div>
            <div class="metric-card__label">{title}</div>
            {caption_html}
        </div>
        """
    )


def render_hero(jobs) -> None:
    """Render the hero banner summarizing live production context."""
    job_count = jobs["job_id"].nunique()
    avg_surface = jobs["surface_score"].mean() if "surface_score" in jobs else 0
    avg_duration = jobs["duration_s"].mean() / 60 if "duration_s" in jobs else 0

    st.markdown(
        dedent(
            f"""
            <div class="hero-card">
                <div class="hero-heading">Craft Stone. Capture Margin. Course-Correct in Real Time.</div>
                <div class="hero-subtitle">
                    Monumental's fabrication intelligence dashboard blends machine telemetry, cost analytics,
                    and ML-ready features into one luminous control surface.
                </div>
                <div class="hero-badges">
                    <span class="hero-badge">{job_count} Active Programs</span>
                    <span class="hero-badge">{avg_duration:0.1f}m Avg Cycle</span>
                    <span class="hero-badge">Surface score {avg_surface:0.1f}</span>
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
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
    with st.container():
        st.subheader("How Data Flows Across the Fabrication Platform")
        image_path = Path(__file__).resolve().parent / "assets" / "system_diagram.png"
        if image_path.exists():
            st.image(str(image_path), use_column_width=True)
        else:
            st.warning(
                "System diagram not found. Add app/assets/system_diagram.png to display it."
            )

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
    avg_minutes = jobs["duration_s"].mean() / 60
    job_count = jobs["job_id"].nunique()
    defect_total = jobs["defect_count"].sum() if "defect_count" in jobs else 0
    defects_per_job = defect_total / job_count if job_count else 0

    cards = [
        {
            "title": "Avg Carve Time",
            "value": f"{avg_minutes:0.1f} min",
            "icon": "⏱",
            "caption": "Benchmarking path-to-part efficiency",
        },
        {
            "title": "Total Jobs",
            "value": f"{job_count}",
            "icon": "🧱",
            "caption": "Unique fabrication programs executed",
        },
        {
            "title": "Surface Score",
            "value": f"{jobs['surface_score'].mean():0.1f} / 100",
            "icon": "✨",
            "caption": "Average finish quality across recorded runs",
        },
        {
            "title": "Profit Margin",
            "value": f"{features['profit_margin'].mean():0.1%}",
            "icon": "💹",
            "caption": f"Defects per job: {defects_per_job:0.2f}",
        },
    ]

    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    for card in cards:
        st.markdown(render_metric_card(**card), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_process_analytics(features):
    """Render process analytics visuals."""
    st.subheader("Process Analytics")
    st.caption("Understand how upstream choices influence carve time, energy and surface finish.")
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

    st.markdown('<div class="quality-progress">', unsafe_allow_html=True)
    for source, pct in completeness.items():
        pct_clamped = max(0, min(pct, 100))
        st.markdown(
            f"""
            <div class="quality-progress__row">
                <div class="quality-progress__label">{source}</div>
                <div class="quality-progress__bar">
                    <div class="quality-progress__fill" style="width: {pct_clamped}%;"></div>
                </div>
                <div class="quality-progress__value">{pct}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

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
    configure_visual_defaults()
    inject_custom_css()
    try:
        jobs, features, quality = load_data()
    except FileNotFoundError as exc:
        st.error(
            f"{exc}\\n\\nRun the data generation + ETL scripts before launching the dashboard."
        )
        return

    render_hero(jobs)

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
