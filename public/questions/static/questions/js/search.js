document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector('input[type="search"]');
    if (!searchInput) return;

    // Создаём обёртку
    const wrapper = document.createElement("div");
    wrapper.className = "search-wrapper";
    searchInput.parentNode.insertBefore(wrapper, searchInput);
    wrapper.appendChild(searchInput);

    // Создаём выпадающий список
    const dropdown = document.createElement("div");
    dropdown.className = "search-dropdown";
    dropdown.style.display = "none";
    wrapper.appendChild(dropdown);

    let debounceTimer = null;

    searchInput.addEventListener("input", function () {
        const query = this.value.trim();

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            dropdown.style.display = "none";
            return;
        }

        debounceTimer = setTimeout(function () {
            fetch("/search/?q=" + encodeURIComponent(query))
                .then((response) => response.json())
                .then((data) => {
                    if (data.results.length === 0) {
                        dropdown.innerHTML =
                            '<div class="search-item no-results">Ничего не найдено</div>';
                        dropdown.style.display = "block";
                        return;
                    }

                    dropdown.innerHTML = data.results
                        .map(
                            (item) =>
                                `<a href="${item.url}" class="search-item">${item.title}</a>`
                        )
                        .join("");
                    dropdown.style.display = "block";
                });
        }, 300);
    });

    searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
        }
    });

    document.addEventListener("click", function (e) {
        if (!wrapper.contains(e.target)) {
            dropdown.style.display = "none";
        }
    });
});