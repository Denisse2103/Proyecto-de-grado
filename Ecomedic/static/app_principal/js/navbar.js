// app_principal/static/app_principal/js/navbar.js

const mobileMenu = document.getElementById('mobile-menu');
const navbarMenu = document.querySelector('.navbar-menu');

mobileMenu.addEventListener('click', () => {
    navbarMenu.classList.toggle('active');
    mobileMenu.classList.toggle('open');
});

/* Opcional: Cerrar el menú cuando se hace clic fuera de él */
window.addEventListener('click', (e) => {
    if (!navbarMenu.contains(e.target) && !mobileMenu.contains(e.target)) {
        navbarMenu.classList.remove('active');
        mobileMenu.classList.remove('open');
    }
});
