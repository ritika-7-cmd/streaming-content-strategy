"""
Exploratory Data Analysis
Streaming Content Strategy Analysis
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cleaned_streaming_titles.csv")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["font.size"] = 11


def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def platform_overview(df):
    print("=" * 60)
    print("PLATFORM OVERVIEW")
    print("=" * 60)
    summary = df.groupby("platform").agg(
        total_titles=("title", "count"),
        movies=("content_type", lambda x: (x == "Movie").sum()),
        tv_shows=("content_type", lambda x: (x == "TV Show").sum()),
        avg_release_year=("release_year", "mean"),
        earliest=("release_year", "min"),
        latest=("release_year", "max"),
    ).round(1)
    summary["movie_pct"] = (summary["movies"] / summary["total_titles"] * 100).round(1)
    summary["tv_pct"] = (summary["tv_shows"] / summary["total_titles"] * 100).round(1)
    print(summary)
    return summary


def plot_content_mix(df):
    """Movies vs TV Shows by platform."""
    fig, ax = plt.subplots(figsize=(9, 5))
    mix = df.groupby(["platform", "content_type"]).size().unstack(fill_value=0)
    mix.plot(kind="bar", stacked=True, ax=ax, color=["#1f77b4", "#ff7f0e"])
    ax.set_title("Content Mix: Movies vs TV Shows by Platform", fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Number of Titles")
    ax.legend(title="Type")
    plt.xticks(rotation=0)
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "01_content_mix.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_volume_by_year(df):
    """Titles by release year (last 25 years)."""
    recent = df[df["release_year"] >= 2000]
    fig, ax = plt.subplots(figsize=(12, 5))
    yearly = recent.groupby(["release_year", "platform"]).size().unstack(fill_value=0)
    yearly.plot(ax=ax, marker="o", linewidth=2)
    ax.set_title("Content Volume by Release Year (2000+)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Release Year")
    ax.set_ylabel("Number of Titles")
    ax.legend(title="Platform")
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "02_volume_by_year.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_top_genres(df, top_n=10):
    """Top primary genres overall and by platform."""
    # Overall
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    top_genres = df["primary_genre"].value_counts().head(top_n)
    sns.barplot(x=top_genres.values, y=top_genres.index, ax=axes[0], palette="viridis")
    axes[0].set_title(f"Top {top_n} Primary Genres (All Platforms)", fontweight="bold")
    axes[0].set_xlabel("Count")

    # By platform - normalized
    genre_platform = (
        df.groupby(["platform", "primary_genre"])
        .size()
        .reset_index(name="count")
    )
    # Take top genres overall and pivot
    top_list = top_genres.index.tolist()
    filtered = genre_platform[genre_platform["primary_genre"].isin(top_list)]
    pivot = filtered.pivot(index="primary_genre", columns="platform", values="count").fillna(0)
    pivot = pivot.loc[top_list]  # keep order
    pivot.plot(kind="barh", ax=axes[1], width=0.8)
    axes[1].set_title(f"Top Genres by Platform", fontweight="bold")
    axes[1].set_xlabel("Count")
    axes[1].legend(title="Platform")

    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "03_top_genres.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_rating_distribution(df):
    """Content rating distribution."""
    # Clean ratings a bit
    df = df.copy()
    df["rating_clean"] = df["rating"].fillna("Unknown").astype(str).str.strip()
    # Focus on common ones
    common = df["rating_clean"].value_counts().head(12).index
    filtered = df[df["rating_clean"].isin(common)]

    fig, ax = plt.subplots(figsize=(11, 5))
    rating_counts = filtered.groupby(["rating_clean", "platform"]).size().unstack(fill_value=0)
    rating_counts.plot(kind="bar", ax=ax, width=0.8)
    ax.set_title("Content Rating Distribution by Platform", fontsize=14, fontweight="bold")
    ax.set_xlabel("Rating")
    ax.set_ylabel("Count")
    ax.legend(title="Platform")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "04_rating_distribution.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def plot_movie_runtime(df):
    """Movie runtime distribution."""
    movies = df[(df["content_type"] == "Movie") & (df["duration_unit"] == "min")].copy()
    movies = movies[movies["duration_value"].between(40, 240)]  # reasonable range

    fig, ax = plt.subplots(figsize=(10, 5))
    for platform in movies["platform"].unique():
        subset = movies[movies["platform"] == platform]["duration_value"]
        sns.kdeplot(subset, ax=ax, label=platform, fill=True, alpha=0.3)
    ax.set_title("Movie Runtime Distribution (minutes)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Runtime (min)")
    ax.legend(title="Platform")
    plt.tight_layout()
    path = os.path.join(REPORTS_DIR, "05_movie_runtime.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def generate_insights(df):
    """Print key business insights."""
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)

    total = len(df)
    print(f"\n1. Total titles analyzed: {total:,}")

    for plat in df["platform"].unique():
        sub = df[df["platform"] == plat]
        movie_pct = (sub["content_type"] == "Movie").mean() * 100
        print(f"\n2. {plat}:")
        print(f"   - Titles: {len(sub):,}")
        print(f"   - Movies: {movie_pct:.1f}% | TV Shows: {100-movie_pct:.1f}%")
        top_g = sub["primary_genre"].value_counts().head(3)
        print(f"   - Top genres: {', '.join(top_g.index.tolist())}")

    # Genre concentration
    print("\n3. Genre Strategy Observations:")
    print("   - Amazon Prime has the largest catalog (volume play).")
    print("   - Disney+ is heavily skewed toward Family / Animation / Kids content.")
    print("   - Netflix shows a more balanced Drama / Comedy / International mix.")

    print("\n4. Limitations:")
    print("   - No official 'Originals' flag in public data → cannot precisely measure originals ratio.")
    print("   - Catalogs are point-in-time snapshots (approx. 2021 era for many rows).")
    print("   - Missing true viewership / engagement metrics.")


def main():
    df = load_data()
    print(f"Loaded cleaned data: {df.shape}")

    platform_overview(df)
    plot_content_mix(df)
    plot_volume_by_year(df)
    plot_top_genres(df)
    plot_rating_distribution(df)
    plot_movie_runtime(df)
    generate_insights(df)

    print("\n✅ EDA complete. Charts saved in /reports/")


if __name__ == "__main__":
    main()
