document.addEventListener("DOMContentLoaded", () => {

    // 1️⃣ Contact Form Validation
    const contactForm = document.querySelector("#contact-form");
    if (contactForm) {
        contactForm.addEventListener("submit", (e) => {
            const name = contactForm.querySelector('input[name="name"]').value.trim();
            const email = contactForm.querySelector('input[name="email"]').value.trim();
            const message = contactForm.querySelector('textarea[name="message"]').value.trim();
            let valid = true;
            let errors = [];

            if (name === "") {
                valid = false;
                errors.push("Name is required.");
            }

            if (email === "" || !/^\S+@\S+\.\S+$/.test(email)) {
                valid = false;
                errors.push("A valid email is required.");
            }

            if (message === "") {
                valid = false;
                errors.push("Message cannot be empty.");
            }

            if (!valid) {
                e.preventDefault();
                alert(errors.join("\n"));
            }
        });
    }

    // 2️⃣ Live Search Filter for Articles
    const searchInput = document.querySelector(".search-filter-form input[name='search']");
    const articleCards = document.querySelectorAll(".article-card");

    if (searchInput && articleCards.length > 0) {
        searchInput.addEventListener("input", () => {
            const query = searchInput.value.toLowerCase();
            articleCards.forEach(card => {
                const title = card.querySelector("h2").textContent.toLowerCase();
                const content = card.querySelector("p").textContent.toLowerCase();
                if (title.includes(query) || content.includes(query)) {
                    card.style.display = "";
                } else {
                    card.style.display = "none";
                }
            });
        });
    }

});
