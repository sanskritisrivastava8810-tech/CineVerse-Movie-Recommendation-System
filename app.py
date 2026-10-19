from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash
)

import os
import sqlite3
import pandas as pd

from pathlib import Path

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. FLASK APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-only-change-this-before-deployment"
)

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "users.db"

DATA_FILE = BASE_DIR / "data" / "movies.csv"


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# ==========================================
# 3. INITIALIZE DATABASE
# ==========================================

def initialize_database():
    connection = get_db_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_premium INTEGER NOT NULL DEFAULT 0
            )
        """)

        connection.commit()

    finally:
        connection.close()


# Initialize database before handling requests
initialize_database()


# ==========================================
# 4. LOAD MOVIES FROM CSV
# ==========================================

def load_movies():

    if not DATA_FILE.exists():
        return pd.DataFrame(
            columns=[
                "title",
                "genre",
                "description",
                "rating",
                "poster"
            ]
        )

    df = pd.read_csv(DATA_FILE)

    required_columns = [
        "title",
        "genre",
        "description",
        "rating",
        "poster"
    ]

    for column in required_columns:
        if column not in df.columns:
            df[column] = ""

    return df.fillna("")


# ==========================================
# 5. MOVIE RECOMMENDATION ALGORITHM
# ==========================================

def recommend_movies(movie_title, movies, limit=6):

    if movies.empty:
        return []

    titles = movies["title"].astype(str).str.strip()

    matches = (
        titles.str.casefold()
        == movie_title.strip().casefold()
    )

    if not matches.any():
        return []

    features = (
        movies["genre"].astype(str)
        + " "
        + movies["description"].astype(str)
    )

    try:
        vectorizer = CountVectorizer(
            stop_words="english"
        )

        matrix = vectorizer.fit_transform(features)

        similarity = cosine_similarity(matrix)

    except ValueError:
        return []

    movie_index = matches[matches].index[0]

    scores = list(
        enumerate(similarity[movie_index])
    )

    scores.sort(
        key=lambda item: item[1],
        reverse=True
    )

    recommendations = []

    for index, score in scores:

        if index == movie_index:
            continue

        movie = movies.iloc[index].to_dict()

        movie["similarity"] = round(
            float(score) * 100,
            1
        )

        recommendations.append(movie)

        if len(recommendations) >= limit:
            break

    return recommendations


# ==========================================
# 6. HOME PAGE
# ==========================================

@app.route("/")
def home():

    movies = load_movies()

    return render_template(
        "index.html",
        movies=movies.to_dict("records")
    )


# ==========================================
# 7. MOVIE RECOMMENDATION API
# ==========================================

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()

    if not title:
        return jsonify({
            "error": "Please enter a movie title."
        }), 400

    movies = load_movies()

    if movies.empty:
        return jsonify({
            "error": (
                "Movie dataset is empty. "
                "Please add movies to data/movies.csv."
            )
        }), 400

    results = recommend_movies(
        title,
        movies
    )

    if not results:
        return jsonify({
            "error": "Movie not found. Please try another title."
        }), 404

    return jsonify({
        "recommendations": results
    })


# ==========================================
# 8. USER REGISTRATION
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if not name or not email or not password:

            flash(
                "Please fill in all fields.",
                "error"
            )

            return render_template("register.html")

        if len(password) < 8:

            flash(
                "Password must be at least 8 characters.",
                "error"
            )

            return render_template("register.html")

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO users (
                    name,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    generate_password_hash(password)
                )
            )

            connection.commit()

            flash(
                "Account created successfully. Please log in.",
                "success"
            )

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:

            flash(
                "An account with this email already exists.",
                "error"
            )

        finally:
            connection.close()

    return render_template("register.html")


# ==========================================
# 9. USER LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        connection = get_db_connection()

        try:

            user = connection.execute(
                """
                SELECT *
                FROM users
                WHERE email = ?
                """,
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if (
            user
            and check_password_hash(
                user["password_hash"],
                password
            )
        ):

            session.clear()

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            return redirect(url_for("home"))

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# ==========================================
# 10. USER LOGOUT
# ==========================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home"))


# ==========================================
# 11. PREMIUM PAGE
# ==========================================

@app.route("/premium")
def premium():

    return render_template(
        "premium.html",
        logged_in=bool(session.get("user_id"))
    )


# ==========================================
# 12. RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)