// main.js - Biblioteca Online

document.addEventListener("DOMContentLoaded", () => {
    console.log("📚 Biblioteca Online carregada!");

    // ====== Navbar mobile toggle ======
    const navbarToggler = document.querySelector(".navbar-toggler");
    const navbarCollapse = document.querySelector("#navbarNav");

    if (navbarToggler) {
        navbarToggler.addEventListener("click", () => {
            navbarCollapse.classList.toggle("show");
        });
    }

    // ====== Smooth scroll para âncoras ======
    const scrollLinks = document.querySelectorAll('a[href^="#"]');
    scrollLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute("href"));
            if (target) {
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

    // ====== Alertas dinâmicos ======
    const alertCloseButtons = document.querySelectorAll(".alert .btn-close");
    alertCloseButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            btn.parentElement.style.display = "none";
        });
    });

    // ====== Formulário de pesquisa ======
    const searchForm = document.querySelector("#searchForm");
    if (searchForm) {
        searchForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const query = searchForm.querySelector("input[name='q']").value.trim();
            if (query) {
                // Aqui você pode redirecionar ou chamar API
                alert(`🔎 Procurando por: "${query}"`);
            } else {
                alert("Digite algo para pesquisar!");
            }
        });
    }
});
