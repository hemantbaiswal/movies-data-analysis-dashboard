"""
Movies Data Analysis Dashboard
Run with: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Movies Data Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1c1f26;
        border: 1px solid #2a2e37;
        border-radius: 10px;
        padding: 15px 20px;
    }
    div[data-testid="stMetricLabel"] { color: #9aa0ab; }
    h1, h2, h3 { color: #f5f5f5; }
    .block-container { padding-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

ACCENT = "#e50914"  # Netflix-style red
PALETTE = px.colors.sequential.Reds_r


# ----------------------------------------------------------------------------
# Data loading & cleaning (mirrors the notebook's cleaning steps)
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str = "movies_dataset.csv") -> pd.DataFrame:
    df = pd.read_csv(path, lineterminator="\n")

    # Drop unused columns
    df = df.drop(columns=["Overview", "Original_Language", "Poster_Url"])

    # Cast Release_Date -> datetime -> year
    df["Release_Date"] = pd.to_datetime(df["Release_Date"], errors="coerce")
    df = df.dropna(subset=["Release_Date"])
    df["Year"] = df["Release_Date"].dt.year

    # Categorize Vote_Average into quartile buckets
    labels = ["not_popular", "below_avg", "average", "popular"]
    edges = [
        df["Vote_Average"].min(),
        df["Vote_Average"].quantile(0.25),
        df["Vote_Average"].quantile(0.50),
        df["Vote_Average"].quantile(0.75),
        df["Vote_Average"].max(),
    ]
    df["Vote_Category"] = pd.cut(
        df["Vote_Average"], edges, labels=labels, duplicates="drop"
    )

    # Split + explode Genre
    df["Genre"] = df["Genre"].str.split(", ")
    df = df.explode("Genre").reset_index(drop=True)
    df["Genre"] = df["Genre"].astype("category")
    df = df.dropna(subset=["Genre"])

    return df


df = load_data()

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.title("🎬 Filters")

genres = sorted(df["Genre"].dropna().unique().tolist())
selected_genres = st.sidebar.multiselect("Genre", genres, default=[])

year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Release year", year_min, year_max, (max(year_min, 1990), year_max)
)

vote_cats = ["not_popular", "below_avg", "average", "popular"]
selected_votes = st.sidebar.multiselect("Vote category", vote_cats, default=[])

filtered = df[df["Year"].between(*year_range)]
if selected_genres:
    filtered = filtered[filtered["Genre"].isin(selected_genres)]
if selected_votes:
    filtered = filtered[filtered["Vote_Category"].isin(selected_votes)]

st.sidebar.markdown("---")
st.sidebar.caption(f"{filtered['Title'].nunique():,} unique movies match your filters")

# ----------------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------------
st.title("🎬 Movies Data Analysis Dashboard")
st.caption("Exploring popularity, genres, and votes across the TMDB movie catalog")

unique_movies = filtered.drop_duplicates(subset=["Title", "Release_Date"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Movies", f"{unique_movies.shape[0]:,}")
col2.metric("Avg. Popularity", f"{unique_movies['Popularity'].mean():,.1f}")
col3.metric("Avg. Vote Score", f"{unique_movies['Vote_Average'].mean():.2f} / 10")
col4.metric("Genres Represented", f"{filtered['Genre'].nunique()}")

st.markdown("---")

# ----------------------------------------------------------------------------
# Row 1: Genre distribution + Vote category distribution
# ----------------------------------------------------------------------------
row1_col1, row1_col2 = st.columns([3, 2])

with row1_col1:
    st.subheader("Most Frequent Genres")
    genre_counts = (
        filtered["Genre"].value_counts().reset_index()
    )
    genre_counts.columns = ["Genre", "Count"]
    fig_genre = px.bar(
        genre_counts.sort_values("Count"),
        x="Count",
        y="Genre",
        orientation="h",
        color="Count",
        color_continuous_scale=PALETTE,
        height=500,
    )
    fig_genre.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=0, r=10, t=10, b=0),
    )
    st.plotly_chart(fig_genre, use_container_width=True)

with row1_col2:
    st.subheader("Vote Category Split")
    vote_counts = filtered["Vote_Category"].value_counts().reset_index()
    vote_counts.columns = ["Category", "Count"]
    fig_vote = px.pie(
        vote_counts,
        names="Category",
        values="Count",
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Reds_r,
    )
    fig_vote.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2),
    )
    st.plotly_chart(fig_vote, use_container_width=True)

# ----------------------------------------------------------------------------
# Row 2: Release year trend
# ----------------------------------------------------------------------------
st.subheader("Movies Released Per Year")
year_counts = (
    unique_movies.groupby("Year").size().reset_index(name="Count")
)
fig_year = px.area(
    year_counts,
    x="Year",
    y="Count",
    color_discrete_sequence=[ACCENT],
)
fig_year.update_traces(line=dict(width=2))
fig_year.update_layout(
    template="plotly_dark",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=10, t=10, b=0),
    height=350,
)
st.plotly_chart(fig_year, use_container_width=True)

# ----------------------------------------------------------------------------
# Row 3: Top popular / least popular movies + Popularity vs Votes scatter
# ----------------------------------------------------------------------------
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("Top 10 Most Popular Movies")
    top10 = (
        unique_movies.sort_values("Popularity", ascending=False)
        .drop_duplicates(subset="Title")
        .head(10)[["Title", "Popularity", "Vote_Average", "Year"]]
    )
    fig_top = px.bar(
        top10.sort_values("Popularity"),
        x="Popularity",
        y="Title",
        orientation="h",
        color="Popularity",
        color_continuous_scale=PALETTE,
        height=400,
    )
    fig_top.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
        margin=dict(l=0, r=10, t=10, b=0),
    )
    st.plotly_chart(fig_top, use_container_width=True)

with row3_col2:
    st.subheader("Popularity vs. Vote Average")
    sample = unique_movies.sample(min(1500, len(unique_movies)), random_state=1)
    fig_scatter = px.scatter(
        sample,
        x="Vote_Average",
        y="Popularity",
        color="Vote_Category",
        hover_data=["Title"],
        color_discrete_sequence=px.colors.sequential.Reds_r,
        height=400,
    )
    fig_scatter.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------------------------------------------
# Data table
# ----------------------------------------------------------------------------
st.markdown("---")
with st.expander("🔍 Browse the filtered data"):
    st.dataframe(
        unique_movies[
            ["Title", "Year", "Genre", "Popularity", "Vote_Average", "Vote_Category"]
        ].sort_values("Popularity", ascending=False),
        use_container_width=True,
        height=400,
    )
