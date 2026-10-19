# 🎬 Movie Recommendation System

A web-based Movie Recommendation System that recommends movies based on their genres and descriptions. It helps users discover movies similar to the ones they enjoy.

## ✨ Features

* Search for movies by title.
* Get recommendations for similar movies.
* Display movie posters, ratings, genres, and descriptions.
* Filter movies by genre.
* Handle invalid movie searches with error messages.
* Responsive and user-friendly interface.

## 🛠️ Technologies Used

* **Python** — Recommendation logic
* **Flask** — Backend web framework
* **Pandas** — Movie dataset processing
* **Scikit-learn** — Text vectorization and similarity calculation
* **HTML** — Web page structure
* **CSS** — Styling and responsive design
* **JavaScript** — Search and interactive features

## 📂 Project Structure

```text
Movie-Recommendation-System/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── movies.csv
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
└── venv/
```

**Note:** The `venv/` directory is used for the local Python environment and should not be uploaded to GitHub.

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the Project Folder

```bash
cd Movie-Recommendation-System
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows Command Prompt:

```bash
venv\Scripts\activate
```

For Git Bash:

```bash
source venv/Scripts/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

Open the local address displayed in your terminal in a web browser.

## 🧠 How It Works

1. The application loads movie information from a CSV dataset.
2. Movie genres and descriptions are combined into text features.
3. Scikit-learn's `CountVectorizer` converts the text into numerical vectors.
4. Cosine similarity calculates how similar movies are.
5. The application displays recommendations for the selected movie.

## 📊 Dataset

The application uses a CSV file containing movie titles, genres, descriptions, ratings, and poster URLs.

Ensure that `data/movies.csv` is present before running the application.

## 🚀 Future Improvements

* Integrate a larger movie dataset.
* Add user accounts and personalized recommendations.
* Improve movie search with autocomplete.
* Deploy the application online.
* Add more advanced recommendation techniques.

## 👩‍💻 Author

**Sanskriti Srivastava**

B.Tech — Computer Science and Engineering

## 📄 License

This project is intended for educational and learning purposes.
