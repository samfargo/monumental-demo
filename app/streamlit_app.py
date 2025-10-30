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

# Custom CSS for beautiful aesthetics
st.markdown(
    """
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin: 1rem;
    }
    
    /* Header styling */
    h1 {
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
        letter-spacing: -1px;
    }
    
    h2 {
        color: #2d3748;
        font-weight: 600;
        font-size: 1.75rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    h3 {
        color: #4a5568;
        font-weight: 600;
        margin-top: 1rem !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #4a5568;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 12px rgba(102, 126, 234, 0.15);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        color: #4a5568;
        font-weight: 500;
        padding: 0 24px;
        transition: all 0.2s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0;
        color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    .stProgress > div > div {
        background-color: #e2e8f0;
        border-radius: 10px;
    }
    
    /* Images */
    img {
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    
    /* Code blocks */
    code {
        background-color: #f7fafc;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #667eea;
        font-weight: 500;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #718096;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 2px solid #e2e8f0;
        font-size: 0.9rem;
    }
    
    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Color palette for charts
CHART_COLORS = {
    "primary": ["#667eea", "#764ba2", "#f093fb", "#4facfe"],
    "gradient": ["#667eea", "#7b68ee", "#8b5cf6", "#9333ea", "#a855f7"],
    "material": {
        "stone": "#667eea",
        "metal": "#f093fb",
        "wood": "#feca57",
        "composite": "#48dbfb",
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
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                🏛️ How Data Flows Across the Fabrication Platform
            </h2>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    image_path = Path(__file__).resolve().parent / "assets" / "system_diagram.png"
    if image_path.exists():
        st.image(str(image_path), use_column_width=True)
    else:
        st.info("💡 System diagram not found. Add `app/assets/system_diagram.png` to display it.")

    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%); 
                    padding: 2rem; 
                    border-radius: 12px; 
                    border-left: 4px solid #667eea;
                    margin-top: 2rem;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
            <p style='font-size: 1.1rem; line-height: 1.8; color: #4a5568; margin: 0;'>
                <strong style='color: #667eea;'>Monumental's fabrication data pipeline</strong> 
                seamlessly stitches together <strong>CAM programming</strong>, 
                <strong>robotic execution</strong>, <strong>quality measurements</strong>, 
                and <strong>ERP context</strong>. Our sophisticated ETL jobs transform these 
                siloed data feeds into a unified data warehouse, enabling powerful shared features 
                for downstream analytics and machine learning applications.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(jobs, features):
    """Render key performance indicators."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                📊 Production Pulse
            </h2>
            <p style='color: #718096; font-size: 1rem;'>Real-time insights into fabrication performance</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    col1, col2, col3, col4 = st.columns(4)
    avg_minutes = jobs["duration_s"].mean() / 60
    
    with col1:
        st.metric(
            "⏱️ Avg Carve Time",
            f"{avg_minutes:0.1f} min",
            delta=None,
        )
    
    with col2:
        st.metric(
            "🏗️ Total Jobs",
            f"{jobs['job_id'].nunique():,}",
            delta=None,
        )
    
    with col3:
        surface_avg = jobs['surface_score'].mean()
        st.metric(
            "✨ Surface Quality",
            f"{surface_avg:0.1f}",
            delta=f"{surface_avg - 80:0.1f} vs target",
            delta_color="normal",
        )
    
    with col4:
        profit_margin = features['profit_margin'].mean()
        st.metric(
            "💰 Profit Margin",
            f"{profit_margin:0.1%}",
            delta=None,
        )


def render_process_analytics(features):
    """Render process analytics visuals."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                🔬 Process Analytics
            </h2>
            <p style='color: #718096; font-size: 1rem;'>Deep dive into fabrication performance metrics</p>
        </div>
        """,
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
            title="<b>Complexity vs. Carve Time</b>",
            color_discrete_sequence=CHART_COLORS["primary"],
        )
        fig1.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            title_font_size=16,
            title_font_color="#2d3748",
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
                "stone_hardness": "Approx. Mohs Hardness",
                "energy_per_cm3": "Energy per cm³ (kWh)",
            },
            title="<b>Energy Load vs. Stone Hardness</b>",
            color_discrete_sequence=CHART_COLORS["gradient"],
        )
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            title_font_size=16,
            title_font_color="#2d3748",
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
        title="<b>Surface Quality vs. Feed Rate Distribution</b>",
        color_continuous_scale=["#667eea", "#764ba2", "#f093fb"],
    )
    fig3.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        title_font_size=16,
        title_font_color="#2d3748",
    )
    st.plotly_chart(fig3, use_container_width=True)


def render_cost_profitability(jobs, features):
    """Render cost and profitability insights."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                💎 Cost & Profitability
            </h2>
            <p style='color: #718096; font-size: 1rem;'>Financial performance across jobs and materials</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    joined = features.merge(
        jobs[["job_id", "defect_count"]], on="job_id", how="left", suffixes=("", "_jobs")
    )
    joined["profit_usd"] = joined["revenue_usd"] - joined["tool_wear_cost_usd"]

    # Display styled dataframe
    st.markdown("##### 📋 Job Financial Details")
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
            title="<b>Total Profit by Stone Type</b>",
            labels={"stone_type": "Stone Type", "profit_usd": "Total Profit (USD)"},
            color_discrete_sequence=CHART_COLORS["gradient"],
        )
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            title_font_size=16,
            title_font_color="#2d3748",
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
            title="<b>Revenue vs. Tool Wear Cost</b>",
            labels={
                "tool_wear_cost_usd": "Tool Wear Cost (USD)",
                "revenue_usd": "Revenue (USD)",
            },
            color_discrete_sequence=CHART_COLORS["primary"],
        )
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            title_font_size=16,
            title_font_color="#2d3748",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


def render_feature_store(features):
    """Render engineered feature list and correlations."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                🤖 ML Feature Store
            </h2>
            <p style='color: #718096; font-size: 1rem;'>Engineered features powering machine learning models</p>
        </div>
        """,
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

    st.markdown("##### 🔧 Available Features")
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border-left: 4px solid #667eea;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                    margin-bottom: 2rem;'>
        """,
        unsafe_allow_html=True,
    )
    
    # Display features in a grid
    cols = st.columns(3)
    for idx, column in enumerate(feature_columns):
        col_idx = idx % 3
        cols[col_idx].markdown(
            f"<div style='padding: 0.5rem; background: white; margin: 0.25rem; "
            f"border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>"
            f"<code style='color: #667eea;'>{column}</code></div>",
            unsafe_allow_html=True,
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Correlation heatmap
    st.markdown("##### 📊 Feature Correlation Matrix")
    numeric_cols = feature_columns + ["duration_s"]
    corr = features[numeric_cols].corr()
    
    fig_corr = px.imshow(
        corr,
        zmin=-1,
        zmax=1,
        color_continuous_scale=["#764ba2", "#ffffff", "#667eea"],
        title="<b>Feature Correlation Analysis</b>",
        aspect="auto",
    )
    fig_corr.update_layout(
        font_family="Inter",
        title_font_size=16,
        title_font_color="#2d3748",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_corr, use_container_width=True)


def render_data_quality(quality_report):
    """Render data quality metrics as progress and status."""
    st.markdown(
        """
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='border: none; font-size: 2rem; color: #2d3748;'>
                ✅ Data Quality Monitoring
            </h2>
            <p style='color: #718096; font-size: 1rem;'>Real-time data validation and completeness tracking</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Completeness metrics
    st.markdown("##### 📈 Data Completeness by Source")
    completeness = quality_report["completeness_percent"]
    
    for source, pct in completeness.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(
                min(int(pct), 100) / 100,
                text=f"**{source.replace('_', ' ').title()}**"
            )
        with col2:
            color = "#48bb78" if pct >= 95 else "#ed8936" if pct >= 80 else "#f56565"
            st.markdown(
                f"<div style='text-align: right; font-size: 1.2rem; font-weight: 600; color: {color};'>"
                f"{pct}%</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Critical metrics
    st.markdown("##### 🎯 Critical Field Validation")
    col1, col2, col3, col4 = st.columns(4)
    
    critical_nulls = quality_report["critical_nulls"]
    
    with col1:
        null_duration = critical_nulls.get("duration_s", 0)
        st.metric(
            "⏱️ Null Duration",
            f"{null_duration}",
            delta=None if null_duration == 0 else "Attention needed",
            delta_color="inverse",
        )
    
    with col2:
        null_revenue = critical_nulls.get("revenue_usd", 0)
        st.metric(
            "💰 Null Revenue",
            f"{null_revenue}",
            delta=None if null_revenue == 0 else "Attention needed",
            delta_color="inverse",
        )
    
    outliers = quality_report["carve_time_outliers"]
    with col3:
        st.metric(
            "⚠️ Time Outliers",
            f"{outliers['count']}",
            delta=None,
        )
    
    tool_validations = quality_report["tool_catalog_validation"]
    with col4:
        st.metric(
            "🔧 Invalid Tools",
            f"{tool_validations['invalid_count']}",
            delta=None,
        )

    # Detailed outlier information
    if outliers['job_ids']:
        st.markdown("##### 🔍 Outlier Details")
        st.info(
            f"**Carve Time Outliers:** Jobs {', '.join(outliers['job_ids'][:5])} "
            f"{'and more...' if len(outliers['job_ids']) > 5 else ''}"
        )

    if tool_validations['unknown_ids']:
        st.warning(
            f"**Unknown Tool IDs:** {', '.join(tool_validations['unknown_ids'][:5])} "
            f"{'and more...' if len(tool_validations['unknown_ids']) > 5 else ''}"
        )


def main():
    """Application entry point."""
    # Beautiful header
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem 0 1rem 0;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem;'>
                🏛️ Fabrication Data Platform
            </h1>
            <p style='font-size: 1.3rem; color: #718096; font-weight: 400; margin-top: 0;'>
                Unifying stone fabrication data for intelligent manufacturing
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    try:
        jobs, features, quality = load_data()
    except FileNotFoundError as exc:
        st.error(
            f"⚠️ **Data Not Found**\n\n{exc}\n\n"
            "Please run the data generation and ETL scripts before launching the dashboard."
        )
        return

    tabs = st.tabs(
        [
            "🏛️ System Overview",
            "📊 KPIs",
            "🔬 Process Analytics",
            "💎 Cost & Profitability",
            "🤖 ML Features",
            "✅ Data Quality",
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

    # Beautiful footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='footer'>
            <div style='max-width: 800px; margin: 0 auto;'>
                <p style='font-weight: 600; color: #4a5568; margin-bottom: 0.5rem;'>
                    Technology Stack
                </p>
                <p style='color: #718096;'>
                    <span style='background: #f7fafc; padding: 0.3rem 0.8rem; border-radius: 20px; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;'>
                        🐍 Python
                    </span>
                    <span style='background: #f7fafc; padding: 0.3rem 0.8rem; border-radius: 20px; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;'>
                        🦆 DuckDB
                    </span>
                    <span style='background: #f7fafc; padding: 0.3rem 0.8rem; border-radius: 20px; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;'>
                        🐼 Pandas
                    </span>
                    <span style='background: #f7fafc; padding: 0.3rem 0.8rem; border-radius: 20px; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;'>
                        📊 Plotly
                    </span>
                    <span style='background: #f7fafc; padding: 0.3rem 0.8rem; border-radius: 20px; 
                                 margin: 0 0.3rem; display: inline-block; margin-bottom: 0.5rem;'>
                        🎈 Streamlit
                    </span>
                </p>
                <p style='color: #a0aec0; font-size: 0.85rem; margin-top: 1rem;'>
                    Synthetic data generation • KUKA robot integration • Real-time fabrication analytics
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
