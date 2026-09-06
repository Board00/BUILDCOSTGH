const token = localStorage.getItem('buildcost_access_token');
const dashboard = document.querySelector('[data-dashboard]');
const message = document.querySelector('.dashboard-message');

const apiRequest = async (path, options = {}) => {
    const response = await fetch(path, { ...options, headers: { ...(options.headers || {}), Authorization: `Bearer ${token}` } });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to load dashboard data.');
    return data;
};

const money = (value) => `GH₵ ${Number(value || 0).toLocaleString('en-GH', { maximumFractionDigits: 0 })}`;
const showError = (error) => { if (message) message.textContent = error.message; };
const logout = async () => {
    document.querySelectorAll('.logout-button').forEach((button) => { button.disabled = true; button.textContent = 'Logging out...'; });
    try {
        await fetch('/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
    } finally {
        localStorage.removeItem('buildcost_access_token');
        window.location.href = '/login';
    }
};
document.querySelectorAll('.logout-button').forEach((button) => button.addEventListener('click', logout));

if (!token && dashboard) window.location.href = '/login';

const renderUserDashboard = async () => {
    const user = await apiRequest('/user');
    if (user.is_admin) {
        window.location.href = '/admin/dashboard';
        return;
    }
    const estimates = await apiRequest('/estimates');
    document.querySelector('[data-user-name]').textContent = user.user_id ? user.message.replace('Welcome, ', '').replace('! You are logged in.', '') : 'builder';
    document.querySelectorAll('[data-estimate-count]').forEach((element) => { element.textContent = element.matches('.section-count') ? `${estimates.length} estimates` : estimates.length; });
    if (estimates.length) {
        document.querySelector('[data-latest-status]').textContent = estimates[0].confidence || 'Ready';
        document.querySelector('[data-estimate-list]').innerHTML = estimates.slice(0, 5).map((estimate) => `<div class="estimate-row"><span class="row-index">#${estimate.id}</span><span><strong>${estimate.user_input.building_type || 'Build estimate'}</strong><small>${estimate.user_input.district || 'Ghana'} &middot; ${estimate.user_input.area || '-'} m²</small></span><strong class="row-total">${money(estimate.total)}</strong><span class="confidence-tag">${estimate.confidence}</span></div>`).join('');
    }
};

const bindEstimateForm = () => {
    const form = document.querySelector('#estimate-form');
    if (!form) return;
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button'); button.disabled = true; button.firstChild.textContent = 'Calculating...';
        const values = new FormData(form);
        const payload = { region: values.get('region'), district: values.get('district'), area: Number(values.get('area')), building_type: values.get('building_type'), finishing: values.get('finishing'), land_owned: values.get('land_owned') === 'on', extras: values.getAll('extras') };
        try {
            const result = await apiRequest('/estimate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
            form.hidden = true; const resultPanel = document.querySelector('.estimate-result'); resultPanel.hidden = false; document.querySelector('[data-result-total]').textContent = money(result.itemized.total); document.querySelector('[data-result-confidence]').textContent = `${result.confidence.level} confidence · Estimate #${result.estimate_id}`; await renderUserDashboard();
        } catch (error) { showError(error); button.disabled = false; button.firstChild.textContent = 'Generate estimate'; }
    });
    document.querySelector('[data-new-estimate]')?.addEventListener('click', () => { form.reset(); form.hidden = false; document.querySelector('.estimate-result').hidden = true; });
};

const renderAdminDashboard = async () => {
    const user = await apiRequest('/user');
    if (!user.is_admin) {
        window.location.href = '/dashboard';
        return;
    }
    const stats = await apiRequest('/admin/dashboard-data');
    Object.entries(stats).forEach(([key, value]) => { document.querySelectorAll(`[data-admin="${key}"]`).forEach((element) => { element.textContent = element.classList.contains('metric-card') ? value : `${value} records`; }); });
    const total = ['materials', 'labor_rates', 'land_prices', 'permits'].reduce((sum, key) => sum + stats[key], 0); document.querySelector('[data-admin-total]').textContent = total;
};

if (dashboard?.dataset.dashboard === 'user') renderUserDashboard().then(bindEstimateForm).catch(showError);
if (dashboard?.dataset.dashboard === 'admin') renderAdminDashboard().catch(showError);
