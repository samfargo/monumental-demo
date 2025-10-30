"""Streamlit dashboard for the Fabrication Data Platform demo."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import utils


st.set_page_config(
    page_title="Demo Fabrication Data Platform | Monumental Labs",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS - Industrial stone fabrication aesthetic
st.markdown(
    """
    <style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    
    /* Global styles - industrial precision */
    * {
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    }
    
    /* Main container - concrete and steel */
    .main {
        background: linear-gradient(180deg, #1a1d23 0%, #2d3748 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: #f5f5f0;
        border: 3px solid #3d4451;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
        margin: 1rem;
    }
    
    /* Headers - architectural precision */
    h1 {
        font-weight: 700;
        color: #1a1d23;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
        text-transform: uppercase;
        border-bottom: 4px solid #b8860b;
    }
    
    h2 {
        color: #1a1d23;
        font-weight: 600;
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3d4451;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    h3, h5 {
        color: #2d3748;
        font-weight: 600;
        margin-top: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem !important;
    }
    
    /* Metric cards - industrial panels */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1d23;
        font-family: 'IBM Plex Mono', monospace;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.75rem;
        font-weight: 600;
        color: #5a6472;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #ffffff, #e8e8e0);
        padding: 1.5rem;
        border: 2px solid #3d4451;
        box-shadow: 
            4px 4px 8px rgba(0, 0, 0, 0.2),
            inset 1px 1px 2px rgba(255, 255, 255, 0.5);
    }
    
    /* Tabs - industrial switches */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #3d4451;
        padding: 0.5rem;
        border: 2px solid #2d3748;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #5a6472;
        color: #e8e8e0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
        padding: 0 20px;
        border: 1px solid #3d4451;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #6b7280;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #b8860b, #daa520);
        color: #1a1d23 !important;
        font-weight: 700;
        border: 2px solid #8b6914;
        box-shadow: inset 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Dataframe - technical readouts */
    .stDataFrame {
        border: 2px solid #3d4451;
        overflow: hidden;
        box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Info boxes - industrial alerts */
    .stAlert {
        border: 2px solid #3d4451;
        border-left: 4px solid #b8860b;
        background-color: #ffffff;
        box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Progress bars - machine indicators */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #b8860b 0%, #daa520 100%);
    }
    
    .stProgress > div > div {
        background-color: #d1d5db;
        border: 1px solid #9ca3af;
    }
    
    /* Images - technical diagrams */
    img {
        border: 3px solid #3d4451;
        box-shadow: 6px 6px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Code blocks - technical specifications */
    code {
        background-color: #2d3748;
        color: #daa520;
        padding: 0.2rem 0.5rem;
        border: 1px solid #3d4451;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #5a6472;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 3px solid #3d4451;
        font-size: 0.85rem;
        background: linear-gradient(145deg, #e8e8e0, #ffffff);
    }
    
    /* Plotly charts - technical graphs */
    .js-plotly-plot {
        border: 2px solid #3d4451;
        box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.2);
        background: #ffffff;
    }
    
    /* Custom panels */
    .industrial-panel {
        background: linear-gradient(145deg, #ffffff, #e8e8e0);
        border: 2px solid #3d4451;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Color palette - stone, metal, and industrial colors
CHART_COLORS = {
    "primary": ["#5a6472", "#8b7355", "#b8860b", "#708090"],
    "gradient": ["#2d3748", "#3d4451", "#5a6472", "#708090", "#8b9098"],
    "stone": ["#8b8680", "#a8a39d", "#c0bcb5", "#d3cfc8"],
    "metal": ["#3d4451", "#5a6472", "#708090", "#8b9098"],
    "material": {
        "stone": "#8b8680",
        "metal": "#708090",
        "wood": "#8b7355",
        "composite": "#5a6472",
    },
}


@st.cache_data(show_spinner=False)
def load_data():
    """Load all warehouse artifacts needed for the dashboard."""
    jobs = utils.load_jobs_integrated()
    features = utils.load_feature_table()
    quality = utils.load_quality_report()
    return jobs, features, quality


def render_system_overview():
    """Render the system overview tab with diagram and narrative."""
    st.markdown("### SYSTEM ARCHITECTURE")
    
    image_path = Path(__file__).resolve().parent / "assets" / "system_diagram.png"
    if image_path.exists():
        st.image(str(image_path), use_column_width=True)
    else:
        st.info("System diagram not found. Add `app/assets/system_diagram.png` to display it.")

    st.markdown(
        """
        <div class='industrial-panel'>
            <p style='font-size: 1rem; line-height: 1.7; color: #2d3748; margin: 0; text-align: justify;'>
                <strong style='color: #1a1d23;'>MONUMENTAL LABS DATA INTEGRATION PLATFORM</strong><br><br>
                This system integrates data streams from CAM programming, robotic execution units, 
                quality inspection sensors, and enterprise resource planning systems. ETL pipelines 
                consolidate disparate data sources into a centralized warehouse architecture, 
                providing standardized feature sets for operational analytics and predictive modeling.
                <br><br>
                <strong style='color: #1a1d23;'>KEY COMPONENTS:</strong> PowerMill toolpath generation, 
                KUKA robotic telemetry, automated quality inspection, and real-time cost tracking.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(jobs, features):
    """Render key performance indicators."""
    st.markdown("### OPERATIONAL METRICS")
    st.markdown(
        "<p style='color: #5a6472; font-size: 0.85rem; margin-bottom: 1.5rem;'>"
        "Real-time fabrication performance indicators</p>",
        unsafe_allow_html=True,
    )
    
    col1, col2, col3, col4 = st.columns(4)
    avg_minutes = jobs["duration_s"].mean() / 60
    
    with col1:
        st.metric(
            "AVG CYCLE TIME",
            f"{avg_minutes:0.1f} min",
            delta=None,
        )
    
    with col2:
        st.metric(
            "JOBS COMPLETED",
            f"{jobs['job_id'].nunique():,}",
            delta=None,
        )
    
    with col3:
        surface_avg = jobs['surface_score'].mean()
        st.metric(
            "SURFACE QUALITY",
            f"{surface_avg:0.1f} / 100",
            delta=f"{surface_avg - 80:0.1f} vs spec",
            delta_color="normal",
        )
    
    with col4:
        profit_margin = features['profit_margin'].mean()
        st.metric(
            "MARGIN",
            f"{profit_margin:0.1%}",
            delta=None,
        )


def render_process_analytics(features):
    """Render process analytics visuals."""
    st.markdown("### PROCESS ANALYSIS")
    st.markdown(
        "<p style='color: #5a6472; font-size: 0.85rem; margin-bottom: 1.5rem;'>"
        "Detailed fabrication performance analysis</p>",
        unsafe_allow_html=True,
    )
    
    scatter1, scatter2 = st.columns(2)

    with scatter1:
        fig1 = px.scatter(
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
            title="<b>TOOLPATH COMPLEXITY vs CYCLE TIME</b>",
            color_discrete_sequence=CHART_COLORS["primary"],
        )
        fig1.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_family="IBM Plex Sans",
            title_font_size=13,
            title_font_color="#1a1d23",
            font_color="#2d3748",
        )
        st.plotly_chart(fig1, use_container_width=True)

    hardness_df = features.copy()
    hardness_df["stone_hardness"] = hardness_df["stone_type"].fillna("").map(utils.stone_hardness_scale)

    with scatter2:
        fig2 = px.scatter(
            hardness_df,
            x="stone_hardness",
            y="energy_per_cm3",
            color="stone_type",
            hover_name="job_id",
            labels={
                "stone_hardness": "Mohs Hardness",
                "energy_per_cm3": "Energy per cm³ (kWh)",
            },
            title="<b>MATERIAL HARDNESS vs ENERGY CONSUMPTION</b>",
            color_discrete_sequence=CHART_COLORS["stone"],
        )
        fig2.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_family="IBM Plex Sans",
            title_font_size=13,
            title_font_color="#1a1d23",
            font_color="#2d3748",
        )
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.density_heatmap(
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
        title="<b>FEED RATE vs SURFACE QUALITY DISTRIBUTION</b>",
        color_continuous_scale=["#3d4451", "#8b8680", "#b8860b"],
    )
    fig3.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font_family="IBM Plex Sans",
        title_font_size=13,
        title_font_color="#1a1d23",
        font_color="#2d3748",
    )
    st.plotly_chart(fig3, use_container_width=True)


def render_cost_profitability(jobs, features):
    """Render cost and profitability insights."""
    st.markdown("### FINANCIAL ANALYSIS")
    st.markdown(
        "<p style='color: #5a6472; font-size: 0.85rem; margin-bottom: 1.5rem;'>"
        "Cost tracking and profitability by job and material type</p>",
        unsafe_allow_html=True,
    )
    
    joined = features.merge(
        jobs[["job_id", "defect_count"]], on="job_id", how="left", suffixes=("", "_jobs")
    )
    joined["profit_usd"] = joined["revenue_usd"] - joined["tool_wear_cost_usd"]

    # Display styled dataframe
    st.markdown("##### JOB COST BREAKDOWN")
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
        ].set_index("job_id").style.format({
            "labor_hours": "{:.2f}",
            "tool_wear_cost_usd": "${:.2f}",
            "revenue_usd": "${:.2f}",
            "profit_usd": "${:.2f}",
            "defect_count": "{:.0f}",
        }).background_gradient(subset=["profit_usd"], cmap="RdYlGn"),
        use_container_width=True,
        height=350,
    )

    # Profit by stone type chart
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            joined.groupby("stone_type")["profit_usd"].sum().reset_index(),
            x="stone_type",
            y="profit_usd",
            color="stone_type",
            title="<b>PROFIT BY MATERIAL TYPE</b>",
            labels={"stone_type": "Material", "profit_usd": "Total Profit (USD)"},
            color_discrete_sequence=CHART_COLORS["stone"],
        )
        fig_bar.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_family="IBM Plex Sans",
            title_font_size=13,
            title_font_color="#1a1d23",
            font_color="#2d3748",
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Revenue vs cost scatter
        fig_scatter = px.scatter(
            joined,
            x="tool_wear_cost_usd",
            y="revenue_usd",
            color="material",
            size="profit_usd",
            hover_data=["job_id", "stone_type"],
            title="<b>REVENUE vs TOOLING COST</b>",
            labels={
                "tool_wear_cost_usd": "Tool Wear Cost (USD)",
                "revenue_usd": "Revenue (USD)",
            },
            color_discrete_sequence=CHART_COLORS["primary"],
        )
        fig_scatter.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_family="IBM Plex Sans",
            title_font_size=13,
            title_font_color="#1a1d23",
            font_color="#2d3748",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


def render_feature_store(features):
    """Render engineered feature list and correlations."""
    st.markdown("### FEATURE ENGINEERING")
    st.markdown(
        "<p style='color: #5a6472; font-size: 0.85rem; margin-bottom: 1.5rem;'>"
        "Machine learning features derived from process data</p>",
        unsafe_allow_html=True,
    )
    
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

    st.markdown("##### AVAILABLE FEATURES")
    st.markdown(
        "<div class='industrial-panel'>",
        unsafe_allow_html=True,
    )
    
    # Display features in a grid
    cols = st.columns(3)
    for idx, column in enumerate(feature_columns):
        col_idx = idx % 3
        cols[col_idx].markdown(
            f"<div style='padding: 0.4rem; background: #ffffff; margin: 0.25rem; "
            f"border: 1px solid #3d4451;'>"
            f"<code>{column}</code></div>",
            unsafe_allow_html=True,
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Correlation heatmap
    st.markdown("##### CORRELATION MATRIX")
    numeric_cols = feature_columns + ["duration_s"]
    corr = features[numeric_cols].corr()
    
    fig_corr = px.imshow(
            corr,
            zmin=-1,
            zmax=1,
        color_continuous_scale=["#3d4451", "#e8e8e0", "#b8860b"],
        title="<b>FEATURE CORRELATION ANALYSIS</b>",
        aspect="auto",
    )
    fig_corr.update_layout(
        font_family="IBM Plex Sans",
        title_font_size=13,
        title_font_color="#1a1d23",
        font_color="#2d3748",
        paper_bgcolor="#ffffff",
    )
    st.plotly_chart(fig_corr, use_container_width=True)


def render_data_quality(quality_report):
    """Render data quality metrics as progress and status."""
    st.markdown("### DATA QUALITY CONTROL")
    st.markdown(
        "<p style='color: #5a6472; font-size: 0.85rem; margin-bottom: 1.5rem;'>"
        "Real-time validation and completeness monitoring</p>",
        unsafe_allow_html=True,
    )
    
    # Completeness metrics
    st.markdown("##### SOURCE DATA COMPLETENESS")
    completeness = quality_report["completeness_percent"]
    
    for source, pct in completeness.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(
                min(int(pct), 100) / 100,
                text=f"**{source.replace('_', ' ').upper()}**"
            )
        with col2:
            color = "#2d5016" if pct >= 95 else "#92400e" if pct >= 80 else "#991b1b"
            st.markdown(
                f"<div style='text-align: right; font-size: 1.1rem; font-weight: 700; color: {color};'>"
                f"{pct}%</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Critical metrics
    st.markdown("##### VALIDATION STATUS")
    col1, col2, col3, col4 = st.columns(4)
    
    critical_nulls = quality_report["critical_nulls"]
    
    with col1:
        null_duration = critical_nulls.get("duration_s", 0)
        st.metric(
            "NULL DURATION",
            f"{null_duration}",
            delta=None if null_duration == 0 else "Check required",
            delta_color="inverse",
        )
    
    with col2:
        null_revenue = critical_nulls.get("revenue_usd", 0)
        st.metric(
            "NULL REVENUE",
            f"{null_revenue}",
            delta=None if null_revenue == 0 else "Check required",
            delta_color="inverse",
        )

    outliers = quality_report["carve_time_outliers"]
    with col3:
        st.metric(
            "TIME OUTLIERS",
            f"{outliers['count']}",
            delta=None,
    )

    tool_validations = quality_report["tool_catalog_validation"]
    with col4:
        st.metric(
            "INVALID TOOLS",
            f"{tool_validations['invalid_count']}",
            delta=None,
        )

    # Detailed outlier information
    if outliers['job_ids']:
        st.markdown("##### ANOMALY DETECTION")
    st.info(
            f"**Cycle Time Anomalies:** Jobs {', '.join(outliers['job_ids'][:5])} "
            f"{'+ {len(outliers["job_ids"]) - 5} more' if len(outliers['job_ids']) > 5 else ''}"
        )

    if tool_validations['unknown_ids']:
        st.warning(
            f"**Unknown Tool IDs:** {', '.join(tool_validations['unknown_ids'][:5])} "
            f"{'+ {len(tool_validations["unknown_ids"]) - 5} more' if len(tool_validations['unknown_ids']) > 5 else ''}"
    )


def main():
    """Application entry point."""
    # Industrial header
    st.markdown(
        """
        <div style='text-align: center; padding: 1.5rem 0 1rem 0; border-bottom: 4px solid #b8860b;'>
            <h1 style='font-size: 2.8rem; margin-bottom: 0.3rem;'>
                FABRICATION DATA PLATFORM
            </h1>
            <p style='font-size: 1rem; color: #5a6472; font-weight: 600; margin-top: 0; 
                      text-transform: uppercase; letter-spacing: 2px;'>
                Monumental Labs • Robotic Stone Manufacturing
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    try:
        jobs, features, quality = load_data()
    except FileNotFoundError as exc:
        st.error(
            f"**DATA NOT FOUND**\n\n{exc}\n\n"
            "Please run the data generation and ETL scripts before launching the dashboard."
        )
        return

    tabs = st.tabs(
        [
            "SYSTEM",
            "METRICS",
            "PROCESS",
            "FINANCIAL",
            "FEATURES",
            "QUALITY",
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

    # Industrial footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='footer'>
            <div style='max-width: 900px; margin: 0 auto;'>
                <p style='font-weight: 700; color: #1a1d23; margin-bottom: 0.8rem; 
                          text-transform: uppercase; letter-spacing: 1px; font-size: 0.9rem;'>
                    Technology Stack
                </p>
                <p style='color: #5a6472; line-height: 1.8;'>
                    <span style='background: #ffffff; padding: 0.4rem 1rem; border: 1px solid #3d4451; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem; 
                                 font-family: IBM Plex Mono; font-size: 0.8rem;'>
                        Python
                    </span>
                    <span style='background: #ffffff; padding: 0.4rem 1rem; border: 1px solid #3d4451; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;
                                 font-family: IBM Plex Mono; font-size: 0.8rem;'>
                        DuckDB
                    </span>
                    <span style='background: #ffffff; padding: 0.4rem 1rem; border: 1px solid #3d4451; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;
                                 font-family: IBM Plex Mono; font-size: 0.8rem;'>
                        Pandas
                    </span>
                    <span style='background: #ffffff; padding: 0.4rem 1rem; border: 1px solid #3d4451; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;
                                 font-family: IBM Plex Mono; font-size: 0.8rem;'>
                        Plotly
                    </span>
                    <span style='background: #ffffff; padding: 0.4rem 1rem; border: 1px solid #3d4451; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;
                                 font-family: IBM Plex Mono; font-size: 0.8rem;'>
                        Streamlit
                    </span>
                </p>
                <p style='color: #5a6472; font-size: 0.8rem; margin-top: 1.2rem; text-transform: uppercase;
                          letter-spacing: 0.5px;'>
                    PowerMill CAM • KUKA Robotic Systems • Real-Time Process Analytics
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
