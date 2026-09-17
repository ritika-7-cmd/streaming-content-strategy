"""
Streamlit Dashboard
Streaming Content Strategy Analysis
Netflix vs Amazon Prime vs Disney+
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Streaming Content Strategy Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paths
DATA_PATH = Path(__file__).parent / "data" / "cleaned_streaming_titles.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def main():
    st.title("🎬 Streaming Content Strategy Analysis")
    st.markdown("**Netflix · Amazon Prime Video · Disney+** | Comparative Catalog Analysis")
    st.markdown("---")

    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    platforms = st.sidebar.multiselect(
        "Platforms",
        options=sorted(df["platform"].unique()),
        default=sorted(df["platform"].unique()),
    )
    content_types = st.sidebar.multiselect(
        "Content Type",
        options=sorted(df["content_type"].unique()),
        default=sorted(df["content_type"].unique()),
    )
    year_range = st.sidebar.slider(
        "Release Year Range",
        min_value=int(df["release_year"].min()),
        max_value=int(df["release_year"].max()),
        value=(2000, int(df["release_year"].max())),
    )

    # Apply filters
    mask = (
        df["platform"].isin(platforms)
        & df["content_type"].isin(content_types)
        & df["release_year"].between(year_range[0], year_range[1])
    )
    filtered = df[mask]

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Titles", f"{len(filtered):,}")
    with col2:
        movie_pct = (filtered["content_type"] == "Movie").mean() * 100 if len(filtered) else 0
        st.metric("Movies %", f"{movie_pct:.1f}%")
    with col3:
        tv_pct = (filtered["content_type"] == "TV Show").mean() * 100 if len(filtered) else 0
        st.metric("TV Shows %", f"{tv_pct:.1f}%")
    with col4:
        st.metric("Platforms Selected", len(platforms))

    st.markdown("---")

    # Row 1: Content Mix + Volume over time
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Content Mix by Platform")
        mix = (
            filtered.groupby(["platform", "content_type"])
            .size()
            .reset_index(name="count")
        )
        fig = px.bar(
            mix,
            x="platform",
            y="count",
            color="content_type",
            barmode="stack",
            color_discrete_map={"Movie": "#1f77b4", "TV Show": "#ff7f0e"},
            labels={"count": "Number of Titles", "platform": ""},
        )
        fig.update_layout(height=400, margin=dict(t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Titles by Release Year")
        yearly = (
            filtered.groupby(["release_year", "platform"])
            .size()
            .reset_index(name="count")
        )
        fig = px.line(
            yearly,
            x="release_year",
            y="count",
            color="platform",
            markers=True,
            labels={"count": "Titles", "release_year": "Year"},
        )
        fig.update_layout(height=400, margin=dict(t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Genres
    st.subheader("Top Primary Genres")
    top_n = st.slider("Number of top genres", 5, 20, 10)
    top_genres = filtered["primary_genre"].value_counts().head(top_n).index.tolist()
    genre_df = (
        filtered[filtered["primary_genre"].isin(top_genres)]
        .groupby(["primary_genre", "platform"])
        .size()
        .reset_index(name="count")
    )
    fig = px.bar(
        genre_df,
        y="primary_genre",
        x="count",
        color="platform",
        orientation="h",
        barmode="group",
        category_orders={"primary_genre": top_genres},
        labels={"count": "Count", "primary_genre": "Genre"},
    )
    fig.update_layout(height=500, margin=dict(t=20, b=20), yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

    # Row 3: Ratings + Runtime
    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Content Ratings")
        rating_counts = (
            filtered["rating"]
            .fillna("Unknown")
            .value_counts()
            .head(12)
            .reset_index()
        )
        rating_counts.columns = ["rating", "count"]
        fig = px.bar(
            rating_counts,
            x="rating",
            y="count",
            labels={"count": "Count", "rating": "Rating"},
            color_discrete_sequence=["#2ca02c"],
        )
        fig.update_layout(height=400, margin=dict(t=20, b=20), xaxis_tickangle=-40)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Movie Runtime Distribution")
        movies = filtered[
            (filtered["content_type"] == "Movie")
            & (filtered["duration_unit"] == "min")
            & (filtered["duration_value"].between(40, 240))
        ]
        if len(movies) > 0:
            fig = px.histogram(
                movies,
                x="duration_value",
                color="platform",
                nbins=30,
                barmode="overlay",
                opacity=0.6,
                labels={"duration_value": "Runtime (minutes)"},
            )
            fig.update_layout(height=400, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No movie runtime data available for current filters.")

    # Key Insights section
    st.markdown("---")
    st.subheader("📌 Key Strategic Insights")
    st.markdown("""
    | Platform | Strategy Snapshot | Catalog Strength |
    |----------|-------------------|------------------|
    | **Amazon Prime** | Volume-first approach | Largest catalog, heavy on Drama & Action movies |
    | **Netflix** | Balanced originals + licensed | Strong Drama/Comedy/Documentary mix, higher TV share |
    | **Disney+** | Franchise & Family focus | Animation, Action-Adventure, Kids & Family content |

    **Observations**
    - Amazon Prime leads in pure title count → library depth strategy.
    - Netflix maintains the highest proportion of TV Shows among the three.
    - Disney+ catalog is intentionally narrower and more focused on brand-safe, family-oriented content.
    - All three platforms show strong growth in content volume after ~2015–2016 (streaming boom era).

    **Limitations**
    - Public datasets lack official “Originals” flags and true viewership numbers.
    - Snapshots are historical (mostly up to ~2021); current catalogs have evolved.
    """)

    st.markdown("---")
    st.caption("Built as a weekend data science project · Data sources: Kaggle public streaming catalogs (Shivam Bansal & community)")


if __name__ == "__main__":
    main()
