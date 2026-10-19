document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("search-form");
    const movieInput = document.getElementById("movie-input");
    const searchButton = document.getElementById("search-button");
    const message = document.getElementById("message");

    const recommendationSection =
        document.getElementById("recommendations");

    const recommendationGrid =
        document.getElementById("recommendation-grid");

    const searchedTitle =
        document.getElementById("searched-title");

    const clearButton =
        document.getElementById("clear-recommendations");

    const genreButtons =
        document.querySelectorAll(".filter-btn");

    const exploreCards =
        document.querySelectorAll(".explore-card");

    const trendingGrid =
        document.getElementById("trending-grid");

    const exploreGrid =
        document.getElementById("explore-grid");

    const filterCount =
        document.getElementById("filter-count");

    const noFilterResults =
        document.getElementById("no-filter-results");

    const focusSearch =
        document.getElementById("focus-search");

    const showAllButton =
        document.getElementById("show-all");


    // SEARCH BAR FOCUS

    if (focusSearch) {
        focusSearch.addEventListener("click", () => {
            movieInput.focus();

            document.getElementById("home")
                .scrollIntoView({ behavior: "smooth" });
        });
    }


    // ESCAPE HTML TO DISPLAY TEXT SAFELY

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;"
            };

            return entities[character];
        });
    }


    // RENDER RECOMMENDATION CARDS

    function renderRecommendations(movies) {
        recommendationGrid.innerHTML = "";

        if (!Array.isArray(movies) || movies.length === 0) {
            recommendationGrid.innerHTML = `
                <div class="empty-state">
                    <h3>No recommendations found</h3>
                    <p>Try searching for another movie.</p>
                </div>
            `;

            return;
        }

        movies.forEach((movie) => {
            const card = document.createElement("article");
            card.className = "movie-card";

            const title = escapeHTML(movie.title);
            const genre = escapeHTML(movie.genre || "Movie");
            const rating = escapeHTML(movie.rating || "N/A");
            const poster = String(movie.poster || "").trim();

            const posterMarkup = poster
                ? `<img class="movie-poster"
                        src="${escapeHTML(poster)}"
                        alt="${title} poster"
                        loading="lazy">`
                : `<div class="poster-placeholder">
                        <span>🎬</span>
                        <p>${title}</p>
                   </div>`;

            card.innerHTML = `
                <div class="poster-wrap">
                    ${posterMarkup}

                    <div class="poster-overlay">
                        <button
                            class="play-button quick-recommend"
                            data-title="${title}"
                            aria-label="Find movies similar to ${title}">
                            ▶
                        </button>
                        <span class="overlay-label">FIND SIMILAR</span>
                    </div>

                    <span class="poster-rating">★ ${rating}</span>
                </div>

                <div class="movie-info">
                    <h3>${title}</h3>
                    <p class="movie-genre">${genre}</p>
                </div>
            `;

            recommendationGrid.appendChild(card);
        });
    }


    // REQUEST MOVIE RECOMMENDATIONS FROM FLASK

    async function findRecommendations(title) {
        const cleanTitle = title.trim();

        if (!cleanTitle) {
            message.textContent = "Please enter a movie title.";
            message.className = "message error";
            return;
        }

        message.textContent = "Finding movies you'll love...";
        message.className = "message";

        searchButton.disabled = true;
        searchButton.textContent = "Searching...";

        try {
            const response = await fetch("/recommend", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: cleanTitle
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(
                    data.error || "Unable to find recommendations."
                );
            }

            renderRecommendations(data.recommendations || []);

            searchedTitle.textContent = cleanTitle;
            recommendationSection.classList.remove("hidden");

            message.textContent = "Your next movie night starts here.";
            message.className = "message";

            recommendationSection.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            message.textContent = error.message;
            message.className = "message error";

            recommendationSection.classList.add("hidden");

        } finally {
            searchButton.disabled = false;
            searchButton.innerHTML = 'Discover <span>→</span>';
        }
    }


    // SEARCH FORM

    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();

        findRecommendations(movieInput.value);
    });


    // QUICK RECOMMEND BUTTONS

    document.addEventListener("click", (event) => {
        const button = event.target.closest(".quick-recommend");

        if (!button) {
            return;
        }

        const title = button.dataset.title;

        if (title) {
            movieInput.value = title;
            findRecommendations(title);
        }
    });


    // CLEAR RECOMMENDATIONS

    clearButton.addEventListener("click", () => {
        recommendationSection.classList.add("hidden");
        recommendationGrid.innerHTML = "";
        movieInput.value = "";
        message.textContent = "";

        document.getElementById("home").scrollIntoView({
            behavior: "smooth"
        });
    });


    // GENRE FILTERS

    function applyGenreFilter(selectedGenre) {
        let visibleCount = 0;

        exploreCards.forEach((card) => {
            const genres = (card.dataset.genre || "")
                .toLowerCase()
                .split(/[,|/]/)
                .map((genre) => genre.trim());

            const matches =
                selectedGenre === "all" ||
                genres.some((genre) =>
                    genre.includes(selectedGenre)
                );

            card.classList.toggle("hidden", !matches);

            if (matches) {
                visibleCount++;
            }
        });

        filterCount.textContent =
            `${visibleCount} movie${visibleCount === 1 ? "" : "s"} found`;

        noFilterResults.classList.toggle(
            "hidden",
            visibleCount !== 0
        );
    }


    genreButtons.forEach((button) => {
        button.addEventListener("click", () => {
            genreButtons.forEach((item) => {
                item.classList.remove("active");
            });

            button.classList.add("active");

            applyGenreFilter(button.dataset.genre || "all");
        });
    });


    // SHOW ALL MOVIES

    showAllButton.addEventListener("click", () => {
        genreButtons.forEach((button) => {
            button.classList.toggle(
                "active",
                button.dataset.genre === "all"
            );
        });

        applyGenreFilter("all");

        exploreGrid.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    });


    // HANDLE BROKEN POSTER LINKS

    document.addEventListener("error", (event) => {
        if (
            event.target instanceof HTMLImageElement &&
            event.target.classList.contains("movie-poster")
        ) {
            const placeholder = document.createElement("div");
            placeholder.className = "poster-placeholder";

            const icon = document.createElement("span");
            icon.textContent = "🎬";

            const title = document.createElement("p");
            title.textContent =
                event.target.alt.replace(/\s+poster$/i, "");

            placeholder.append(icon, title);

            event.target.replaceWith(placeholder);
        }
    }, true);


    // INITIAL FILTER COUNT

    applyGenreFilter("all");
});