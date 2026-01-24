const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});


// modal
function openModal() {
    document.getElementById("modalOverlay").style.display = "flex";
}

function closeModal() {
    document.getElementById("modalOverlay").style.display = "none";
}

// Fechar clicando fora
document.getElementById("modalOverlay").addEventListener("click", function (e) {
    if (e.target.id === "modalOverlay") {
        closeModal();
    }
});
