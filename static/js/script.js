
// ==============================
// SHOPPING CART COUNTER
// ==============================

let cartCount = 0;

const cartCounter = document.getElementById("cartCount");
const addCartButtons = document.querySelectorAll(".add-cart");

addCartButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        cartCount++;

        cartCounter.textContent = cartCount;

        alert("Product added to your cart!");
    });
});


// ==============================
// PRODUCT SEARCH
// ==============================

const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");

function searchProducts() {
    const searchValue = searchInput.value.toLowerCase().trim();

    const products = document.querySelectorAll(".product-card");

    products.forEach(function(product) {
        const productName = product.dataset.name.toLowerCase();

        if (productName.includes(searchValue)) {
            product.style.display = "";
        } else {
            product.style.display = "none";
        }
    });
}

searchButton.addEventListener("click", searchProducts);

searchInput.addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        searchProducts();
    }
});
