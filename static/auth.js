const form = document.querySelector('.auth-form');
const message = document.querySelector('.form-message');

if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button');
        button.disabled = true;
        message.textContent = 'Working...';
        message.className = 'form-message';

        try {
            const isLogin = form.id === 'login-form';
            const body = isLogin
                ? new URLSearchParams(new FormData(form))
                : JSON.stringify(Object.fromEntries(new FormData(form)));
            const response = await fetch(isLogin ? '/login' : '/register', {
                method: 'POST',
                headers: isLogin ? { 'Content-Type': 'application/x-www-form-urlencoded' } : { 'Content-Type': 'application/json' },
                body,
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Something went wrong.');

            if (isLogin) {
                localStorage.setItem('buildcost_access_token', data.access_token);
                const profileResponse = await fetch('/user', {
                    headers: { Authorization: `Bearer ${data.access_token}` },
                });
                const profile = await profileResponse.json();
                if (!profileResponse.ok) throw new Error(profile.detail || 'Unable to load your account.');

                message.textContent = profile.is_admin
                    ? 'Admin account verified. Opening the control room...'
                    : 'You are logged in. Taking you to your workspace...';
                message.classList.add('success');
                const destination = profile.is_admin ? '/admin/dashboard' : '/dashboard';
                window.setTimeout(() => { window.location.href = destination; }, 700);
            } else {
                message.textContent = 'Account created. Redirecting you to log in...';
                message.classList.add('success');
                window.setTimeout(() => { window.location.href = '/login'; }, 900);
            }
        } catch (error) {
            localStorage.removeItem('buildcost_access_token');
            message.textContent = error.message;
            message.classList.add('error');
            button.disabled = false;
        }
    });
}
