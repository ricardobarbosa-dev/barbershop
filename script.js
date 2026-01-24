const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// modal
const openBtn = document.getElementById("openPrices");
const modal = document.getElementById("pricesModal");
const closeBtn = document.getElementById("closePrices");

openBtn.addEventListener("click", (e) => {
    e.preventDefault();
    modal.classList.add("active");
});

closeBtn.addEventListener("click", () => {
    modal.classList.remove("active");
});

modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("active");
    }
});

