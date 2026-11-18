// ~~~~~~~~~~~~~~   CARDS DISPLAY   ~~~~~~~~~~~~~~~~~~ //

console.log("JavaScript is running");

const TOUR_CARD_CONFIG = {
    domestic: {
        cardClass: "domestic-card",
        imageClass: "domestic-card-image",
        contentClass: "domestic-card-content",
        numberClass: "domestic-card-number",
        linkClass: "domestic-card-link",
        searchInputId: "package-search-input",
    },
    international: {
        cardClass: "international-card",
        imageClass: "international-card-image",
        contentClass: "international-card-content",
        numberClass: "international-card-number",
        linkClass: "international-card-link",
        searchInputId: "international-search-input",
    },
};

function createTourElement(tagName, className, text) {
    const element = document.createElement(tagName);
    element.className = className;
    element.textContent = text;
    return element;
}

function createImageTourCard(tour, category, index) {
    const config = TOUR_CARD_CONFIG[category];
    const card = document.createElement("article");
    card.className = config.cardClass;

    const imageContainer = document.createElement("div");
    imageContainer.className = config.imageClass;

    const image = document.createElement("img");
    image.src = tour.image;
    image.alt = tour.name;
    image.loading = "lazy";
    imageContainer.appendChild(image);

    const content = document.createElement("div");
    content.className = config.contentClass;
    content.appendChild(createTourElement(
        "div",
        config.numberClass,
        `${String(index + 1).padStart(2, "0")} / ${tour.region}`
    ));
    content.appendChild(createTourElement("h3", "", tour.name));
    content.appendChild(createTourElement("p", "", tour.description));

    const link = document.createElement("a");
    link.className = config.linkClass;
    link.href = "contact.html";
    link.textContent = tour.cta_label;
    content.appendChild(link);

    card.append(imageContainer, content);
    return card;
}

function createUmrahTourCard(tour, index) {
    const card = document.createElement("article");
    card.className = tour.is_featured
        ? "umrah-card featured-umrah"
        : "umrah-card";

    const top = document.createElement("div");
    top.className = "umrah-card-top";
    top.appendChild(createTourElement(
        "span",
        "umrah-number",
        String(index + 1).padStart(2, "0")
    ));
    top.appendChild(createTourElement("span", "umrah-duration", tour.duration));

    const content = document.createElement("div");
    content.className = "umrah-card-content";

    if (tour.is_featured) {
        content.appendChild(createTourElement("span", "package-badge", "POPULAR"));
    }

    content.appendChild(createTourElement("h3", "", tour.name));
    content.appendChild(createTourElement("p", "", tour.description));

    const features = document.createElement("ul");
    tour.features.forEach((feature) => {
        features.appendChild(createTourElement("li", "", feature));
    });
    content.appendChild(features);

    const link = document.createElement("a");
    link.href = "contact.html";
    link.textContent = `${tour.cta_label} ->`;
    content.appendChild(link);

    card.append(top, content);
    return card;
}

function showTourMessage(container, message) {
    const status = createTourElement("p", "tour-grid-message", message);
    status.setAttribute("role", "status");
    status.style.gridColumn = "1 / -1";
    status.style.textAlign = "center";
    container.replaceChildren(status);
}

function applyTourSearch(container, category) {
    const config = TOUR_CARD_CONFIG[category];

    if (!config) {
        return;
    }

    const input = document.getElementById(config.searchInputId);
    const searchTerm = input?.value.toLowerCase().trim();

    if (!searchTerm) {
        return;
    }

    Array.from(container.children).forEach((card) => {
        card.style.display = card.textContent.toLowerCase().includes(searchTerm)
            ? ""
            : "none";
    });
}

async function loadTourCards() {
    const container = document.querySelector("[data-tour-category]");

    if (!container) {
        return;
    }

    const category = container.dataset.tourCategory;
    showTourMessage(container, "Loading packages...");

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/api/tours?category=${encodeURIComponent(category)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        if (!Array.isArray(data.tours) || data.tours.length === 0) {
            showTourMessage(container, "No packages are available right now.");
            return;
        }

        const cards = data.tours.map((tour, index) => (
            category === "umrah"
                ? createUmrahTourCard(tour, index)
                : createImageTourCard(tour, category, index)
        ));

        container.replaceChildren(...cards);
        applyTourSearch(container, category);
    } catch (error) {
        console.error("Failed to load tour packages:", error);
        showTourMessage(container, "Packages could not be loaded. Please try again later.");
    }
}


async function loadDestinations() {
    const container = document.getElementById("destinations-container");

    if (!container) {
        return;
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/api/destinations");

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();
        const cards = data.destinations.map((destination, index) => {
            const card = document.createElement("article");
            card.className = "destination-card";

            const imageContainer = document.createElement("div");
            imageContainer.className = "destination-image";

            const image = document.createElement("img");
            image.src = destination.image;
            image.alt = destination.name;
            image.loading = "lazy";
            imageContainer.appendChild(image);

            const content = document.createElement("div");
            content.className = "destination-content";

            content.appendChild(createTourElement(
                "span",
                "destination-number",
                String(index + 1).padStart(2, "0")
            ));
            content.appendChild(createTourElement("h3", "", destination.name));
            content.appendChild(createTourElement("p", "", destination.description));
            content.appendChild(createTourElement("p", "", destination.country));
            content.appendChild(createTourElement("p", "", destination.duration));
            content.appendChild(createTourElement("p", "", `₹${destination.price}`));

            const link = document.createElement("a");
            link.href = destination.link || "contact.html";
            link.textContent = `Explore ${destination.name} →`;
            content.appendChild(link);

            card.append(imageContainer, content);
            return card;
        });

        if (cards.length === 0) {
            showTourMessage(container, "No destinations are available right now.");
            return;
        }

        container.replaceChildren(...cards);
    } catch (error) {
        console.error("Failed to load destinations:", error);
        showTourMessage(container, "Destinations could not be loaded. Please try again later.");
    }
}


loadTourCards();
loadDestinations();

// ====================================================================================
//                           SEARCH BAR
// ====================================================================================

document.addEventListener("DOMContentLoaded", function () {

    function setupSearch(inputId, containerSelector, changeGridOnSearch = false) {

        const input = document.getElementById(inputId);

        if (!input) {
            return;
        }

        input.addEventListener("input", function () {

            const container = document.querySelector(containerSelector);

            if (!container) {
                return;
            }

            const searchTerm = input.value.toLowerCase().trim();

            // Change destination grid layout while searching
            
            if (changeGridOnSearch) {
                container.classList.toggle(
                    "is-searching",
                    searchTerm !== ""
                );
            }

            Array.from(container.children).forEach(function (card) {

                const cardText = card.textContent.toLowerCase();

                if (cardText.includes(searchTerm)) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }

            });

        });

    }


    // Destination.html
    setupSearch(
        "destination-search-input",
        "#destinations-container",
        true
    );


    // Internationaltours.html
    setupSearch(
        "international-search-input",
        ".international-grid"
    );

});


// ========================================================
// INTERNATIONAL TOURS SEARCH
// ========================================================

function filterInternationalCards(searchTerm) {

    const cards = document.querySelectorAll(".international-card");

    searchTerm = searchTerm.toLowerCase().trim();

    cards.forEach(function (card) {

        const cardText = card.textContent.toLowerCase();

        if (cardText.includes(searchTerm)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }

    });
}


// ========================================================
// DOMESTIC TOURS SEARCH
// ========================================================

function filterDomesticCards(searchTerm) {

    const cards = document.querySelectorAll(".domestic-card");

    searchTerm = searchTerm.toLowerCase().trim();

    cards.forEach(function (card) {

        const cardText = card.textContent.toLowerCase();

        if (cardText.includes(searchTerm)) {
            card.style.display = "";
        } else {
            card.style.display = "none";
        }

    });
}