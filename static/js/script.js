
// ==========================================
// KOBO GOODS - ANIMATED NOTIFICATIONS
// ==========================================

function showToast(message, type = "success") {
    let toastContainer = document.getElementById("toastContainer");

    if (!toastContainer) {
        toastContainer = document.createElement("div");
        toastContainer.id = "toastContainer";
        toastContainer.className = "toast-container";
        document.body.appendChild(toastContainer);
    }

    const icons = {
        success: "✓",
        error: "✕",
        info: "i"
    };

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    const icon = document.createElement("div");
    icon.className = "toast-icon";
    icon.textContent = icons[type] || icons.info;

    const content = document.createElement("div");
    content.className = "toast-content";

    const heading = document.createElement("strong");
    heading.textContent =
        type === "success" ? "Success!" :
        type === "error" ? "Something went wrong" : "Kobo Goods";

    const description = document.createElement("span");
    description.textContent = message;

    content.appendChild(heading);
    content.appendChild(description);

    const closeButton = document.createElement("button");
    closeButton.className = "toast-close";
    closeButton.type = "button";
    closeButton.textContent = "×";
    closeButton.setAttribute("aria-label", "Close notification");

    const progress = document.createElement("div");
    progress.className = "toast-progress";

    toast.append(icon, content, closeButton, progress);
    toastContainer.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("show");
    });

    let removeTimer = setTimeout(removeToast, 3500);

    function removeToast() {
        clearTimeout(removeTimer);
        toast.classList.remove("show");
        toast.classList.add("hide");

        setTimeout(() => toast.remove(), 350);
    }

    closeButton.addEventListener("click", removeToast);
}


// ==========================================
// SHOPPING CART NOTIFICATION
// ==========================================

// Remember the add-to-cart action across the
// page reload caused by Django's form submission.

document.querySelectorAll(".add-cart").forEach(button => {
    button.addEventListener("click", function () {
        sessionStorage.setItem("koboCartNotification", "true");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const cartNotification = sessionStorage.getItem(
        "koboCartNotification"
    );

    if (cartNotification === "true") {
        sessionStorage.removeItem("koboCartNotification");

        showToast(
            "Your product has been added to your cart.",
            "success"
        );
    }
});


// ==========================================
// PRODUCT SEARCH
// ==========================================

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

function searchProducts() {
    if (!searchInput) return;

    const searchValue = searchInput.value.toLowerCase().trim();
    const products = document.querySelectorAll(".product-card");

    products.forEach(function (product) {
        const productName = (
            product.dataset.name || ""
        ).toLowerCase();

        product.style.display =
            productName.includes(searchValue) ? "" : "none";
    });
}

if (searchButton) {
    searchButton.addEventListener("click", searchProducts);
}

if (searchInput) {
    searchInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            searchProducts();
        }
    });
}
