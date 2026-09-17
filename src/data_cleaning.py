"""
Data Cleaning & Unification Script
Streaming Content Strategy Analysis - Netflix, Amazon Prime, Disney+
"""

import pandas as pd
import numpy as np
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "cleaned_streaming_titles.csv")


def load_and_standardize(path: str, platform: str) -> pd.DataFrame:
    """Load a platform CSV and standardize columns."""
    df = pd.read_csv(path)
    df["platform"] = platform

    # Standard column mapping
    rename_map = {
        "listed_in": "genres",
        "type": "content_type",
    }
    df = df.rename(columns=rename_map)

    # Ensure required columns exist
    required = ["show_id", "content_type", "title", "release_year", "rating", "duration", "genres", "description", "platform"]
    for col in required:
        if col not in df.columns:
            df[col] = np.nan

    # Keep only useful columns
    keep_cols = ["show_id", "content_type", "title", "director", "cast", "country",
                 "date_added", "release_year", "rating", "duration", "genres", "description", "platform"]
    keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[keep_cols]

    return df


def clean_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Extract numeric duration and unit."""
    df = df.copy()
    df["duration"] = df["duration"].astype(str)

    def parse_duration(val):
        if pd.isna(val) or val == "nan":
            return np.nan, np.nan
        val = str(val).strip().lower()
        if "min" in val:
            num = "".join([c for c in val if c.isdigit() or c == "."])
            return float(num) if num else np.nan, "min"
        elif "season" in val:
            num = "".join([c for c in val if c.isdigit() or c == "."])
            return float(num) if num else np.nan, "season"
        else:
            return np.nan, np.nan

    parsed = df["duration"].apply(parse_duration)
    df["duration_value"] = parsed.apply(lambda x: x[0])
    df["duration_unit"] = parsed.apply(lambda x: x[1])
    return df


def extract_main_genre(df: pd.DataFrame) -> pd.DataFrame:
    """Take the first genre as primary genre."""
    df = df.copy()
    df["primary_genre"] = (
        df["genres"]
        .fillna("Unknown")
        .astype(str)
        .str.split(",")
        .str[0]
        .str.strip()
    )
    return df


def clean_year_and_type(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["release_year"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["content_type"] = df["content_type"].str.strip().str.title()
    # Normalize TV Show / Movie labels
    df["content_type"] = df["content_type"].replace({
        "Tv Show": "TV Show",
        "Tv show": "TV Show",
        "Movie": "Movie"
    })
    return df


def main():
    print("Loading datasets...")
    netflix = load_and_standardize(
        os.path.join(DATA_DIR, "netflix_titles_classic.csv"), "Netflix"
    )
    prime = load_and_standardize(
        os.path.join(DATA_DIR, "amazon_prime_titles.csv"), "Amazon Prime"
    )
    disney = load_and_standardize(
        os.path.join(DATA_DIR, "disney_plus_titles.csv"), "Disney+"
    )

    print(f"Netflix: {len(netflix)} rows")
    print(f"Amazon Prime: {len(prime)} rows")
    print(f"Disney+: {len(disney)} rows")

    combined = pd.concat([netflix, prime, disney], ignore_index=True)
    print(f"Combined raw: {len(combined)} rows")

    # Cleaning pipeline
    combined = clean_duration(combined)
    combined = extract_main_genre(combined)
    combined = clean_year_and_type(combined)

    # Drop rows with missing critical fields
    combined = combined.dropna(subset=["title", "content_type", "release_year"])
    combined = combined[combined["release_year"] >= 1920]
    combined = combined[combined["release_year"] <= 2025]

    # Simple is_original heuristic (very rough – based on common knowledge / keywords)
    # Note: True originals flag is not available in these public datasets.
    # We keep a placeholder column for future enhancement.
    combined["is_original_proxy"] = False  # Placeholder

    # Final column order
    final_cols = [
        "platform", "show_id", "title", "content_type", "release_year",
        "rating", "duration_value", "duration_unit", "primary_genre",
        "genres", "country", "date_added", "director", "description"
    ]
    final_cols = [c for c in final_cols if c in combined.columns]
    cleaned = combined[final_cols].copy()

    cleaned.to_csv(OUTPUT_PATH, index=False)
    print(f"\nCleaned dataset saved to: {OUTPUT_PATH}")
    print(f"Final shape: {cleaned.shape}")
    print("\nPlatform distribution:")
    print(cleaned["platform"].value_counts())
    print("\nContent type distribution:")
    print(cleaned["content_type"].value_counts())
    print("\nSample primary genres:")
    print(cleaned["primary_genre"].value_counts().head(10))


if __name__ == "__main__":
    main()
