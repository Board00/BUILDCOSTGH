const form = document.querySelector('.auth-form');
const message = document.querySelector('.form-message');

const readResponse = async (response) => {
    const text = await response.text();
    try { return JSON.parse(text); } catch { return { error: { message: text || 'Request failed.' } }; }
};

if (form) {
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button');
        button.disabled = true;
        message.textContent = 'Working...';
        message.className = 'form-message';

        try {
            const isLogin = form.id === 'login-form';
            const isForgotPassword = form.id === 'forgot-password-form';
            const isResetPassword = form.id === 'reset-password-form';
            const body = isLogin
                ? new URLSearchParams(new FormData(form))
                : JSON.stringify(Object.fromEntries(new FormData(form)));
            const endpoint = isLogin
                ? '/login'
                : isForgotPassword
                    ? '/forgot-password'
                    : isResetPassword
                        ? '/reset-password'
                        : '/register';
            const requestBody = isResetPassword
                ? JSON.stringify({
                    ...Object.fromEntries(new FormData(form)),
                    token: new URLSearchParams(window.location.search).get('token'),
                })
                : body;
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: isLogin ? { 'Content-Type': 'application/x-www-form-urlencoded' } : { 'Content-Type': 'application/json' },
                body: requestBody,
            });
            const data = await readResponse(response);
            if (!response.ok) throw new Error(data.detail || data.error?.message || 'Something went wrong.');

            if (isLogin) {
                localStorage.setItem('buildcost_access_token', data.access_token);
                const profileResponse = await fetch('/user', {
                    headers: { Authorization: `Bearer ${data.access_token}` },
                });
                const profile = await readResponse(profileResponse);
                if (!profileResponse.ok) throw new Error(profile.detail || profile.error?.message || 'Unable to load your account.');

                message.textContent = profile.is_admin
                    ? 'Admin account verified. Opening the control room...'
                    : 'You are logged in. Taking you to your workspace...';
                message.classList.add('success');
                const destination = profile.is_admin ? '/admin/dashboard' : '/dashboard';
                window.setTimeout(() => { window.location.href = destination; }, 700);
            } else if (isForgotPassword) {
                message.textContent = data.message;
                message.classList.add('success');
                button.disabled = false;
            } else if (isResetPassword) {
                message.textContent = 'Password updated. Redirecting you to log in...';
                message.classList.add('success');
                window.setTimeout(() => { window.location.href = '/login'; }, 900);
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
