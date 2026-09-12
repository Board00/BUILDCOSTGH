const menuToggle = document.querySelector('.menu-toggle');
const siteNav = document.querySelector('.site-nav');
const themeToggle = document.querySelector('.theme-toggle');
const savedTheme = localStorage.getItem('buildcost_theme');
const accessToken = localStorage.getItem('buildcost_access_token');
const navLogin = document.querySelector('#nav-login');
const navSignup = document.querySelector('#nav-signup');
const navDashboard = document.querySelector('#nav-dashboard');
const navLogout = document.querySelector('#nav-logout');

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

const updateAuthNavigation = async () => {
    if (!accessToken || !navLogin || !navSignup || !navDashboard || !navLogout) return;
    try {
        const response = await fetch('/user', { headers: { Authorization: `Bearer ${accessToken}` } });
        if (!response.ok) throw new Error('Session expired');
        const user = await response.json();
        navLogin.hidden = true;
        navSignup.hidden = true;
        navDashboard.hidden = false;
        navDashboard.href = user.is_admin ? '/admin/dashboard' : '/dashboard';
        navLogout.hidden = false;
    } catch {
        localStorage.removeItem('buildcost_access_token');
    }
};

navLogout?.addEventListener('click', async () => {
    navLogout.disabled = true;
    const currentToken = localStorage.getItem('buildcost_access_token');
    try {
        await fetch('/logout', { method: 'POST', headers: { Authorization: `Bearer ${currentToken}` } });
    } finally {
        localStorage.removeItem('buildcost_access_token');
        window.location.href = '/login';
    }
});

updateAuthNavigation();
