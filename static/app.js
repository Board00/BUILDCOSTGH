const menuToggle = document.querySelector('.menu-toggle');
const siteNav = document.querySelector('.site-nav');
const themeToggle = document.querySelector('.theme-toggle');
const savedTheme = localStorage.getItem('buildcost_theme');

if (savedTheme === 'dark') document.documentElement.classList.add('dark-mode');

const updateThemeToggle = () => {
    if (!themeToggle) return;
    const darkMode = document.documentElement.classList.contains('dark-mode');
    themeToggle.setAttribute('aria-label', darkMode ? 'Switch to light mode' : 'Switch to dark mode');
    themeToggle.querySelector('.theme-icon').textContent = darkMode ? '☀' : '☾';
    themeToggle.querySelector('.theme-label').textContent = darkMode ? 'Light mode' : 'Dark mode';
};

updateThemeToggle();

themeToggle?.addEventListener('click', () => {
    const darkMode = document.documentElement.classList.toggle('dark-mode');
    localStorage.setItem('buildcost_theme', darkMode ? 'dark' : 'light');
    updateThemeToggle();
});

if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', () => {
        const isOpen = siteNav.classList.toggle('is-open');
        menuToggle.setAttribute('aria-expanded', String(isOpen));
    });
}
