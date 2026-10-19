import ast
from pathlib import Path

import pandas as pd
import kagglehub

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "movies.csv"

print("Searching for the downloaded movie dataset...")

# Download again only if KaggleHub needs to retrieve it.
dataset_path = Path(
    kagglehub.dataset_download("rounakbanik/the-movies-dataset")
)

# Locate the metadata CSV.
csv_files = list(dataset_path.rglob("movies_metadata.csv"))

if not csv_files:
    print("ERROR: movies_metadata.csv was not found.")
    print("Dataset location:", dataset_path)
    raise SystemExit(1)

source_file = csv_files[0]
print("Dataset found:", source_file)
print("Reading movie data...")

df = pd.read_csv(source_file, low_memory=False)

def parse_genres(value):
    try:
        items = ast.literal_eval(value) if isinstance(value, str) else []
        return ", ".join(
            item.get("name", "")
            for item in items
            if isinstance(item, dict) and item.get("name")
        )
    except (ValueError, SyntaxError, TypeError):
        return ""

# Build the website's five-column format.
movies = pd.DataFrame()
movies["title"] = df["title"].fillna("").astype(str).str.strip()
movies["genre"] = df["genres"].apply(parse_genres)
movies["description"] = df["overview"].fillna("").astype(str)

movies["rating"] = pd.to_numeric(
    df["vote_average"], errors="coerce"
).fillna(0)

poster_paths = df["poster_path"].fillna("").astype(str)

movies["poster"] = poster_paths.apply(
    lambda path: (
        "https://image.tmdb.org/t/p/w500" + path
        if path.startswith("/")
        else ""
    )
)

# Remove invalid rows and duplicate titles.
movies = movies[
    (movies["title"] != "")
    & (movies["title"].str.lower() != "nan")
].drop_duplicates(subset=["title"])

# Prefer English, Hindi and Telugu movies when language data is available.
if "original_language" in df.columns:
    language = df["original_language"].fillna("").astype(str).str.lower()
    language = language.loc[movies.index]

    preferred = movies[language.isin(["en", "hi", "te"])]
    others = movies[~language.isin(["en", "hi", "te"])]

    movies = pd.concat([preferred, others])
# Prioritize Hollywood (English), Bollywood (Hindi)
# and Tollywood (Telugu) movies.

language = (
    df.loc[movies.index, "original_language"]
    .fillna("")
    .astype(str)
    .str.lower()
)

english_movies = movies[language == "en"]
hindi_movies = movies[language == "hi"]
telugu_movies = movies[language == "te"]

other_movies = movies[
    ~language.isin(["en", "hi", "te"])
]

# Combine languages in priority order.
movies = pd.concat([
    english_movies,
    hindi_movies,
    telugu_movies,
    other_movies
])

# Keep up to 5,000 movies.
movies = movies.head(5000)



DATA_DIR.mkdir(parents=True, exist_ok=True)
movies.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("\nImport completed successfully!")
print("Total movies imported:", len(movies))
print("CSV saved to:", OUTPUT_FILE)
print("\nFirst 10 movies:")
print(movies["title"].head(10).to_string(index=False))

