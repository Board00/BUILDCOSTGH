let token = localStorage.getItem('buildcost_access_token');
const dashboard = document.querySelector('[data-dashboard]');
const message = document.querySelector('.dashboard-message');
const accountMessage = document.querySelector('.account-message');

const readResponse = async (response) => {
    const text = await response.text();
    try { return JSON.parse(text); } catch { return { error: { message: text || 'Request failed.' } }; }
};

const apiRequest = async (path, options = {}) => {
    const response = await fetch(path, { ...options, headers: { ...(options.headers || {}), Authorization: `Bearer ${token}` } });
    const data = await readResponse(response);
    if (!response.ok) throw new Error(data.detail || data.error?.message || 'Unable to load dashboard data.');
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
const bindAccountSettings = (user) => {
    const form = document.querySelector('#profile-form');
    const username = document.querySelector('#profile-username');
    const deactivateButton = document.querySelector('[data-deactivate-account]');
    if (username) username.value = user.message.replace('Welcome, ', '').replace('! You are logged in.', '');
    form?.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button');
        button.disabled = true;
        try {
            const updated = await apiRequest('/user', { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ username: username.value }) });
            token = updated.access_token;
            localStorage.setItem('buildcost_access_token', token);
            accountMessage.textContent = updated.message;
            accountMessage.className = 'account-message success';
            document.querySelector('[data-user-name]').textContent = username.value;
        } catch (error) { accountMessage.textContent = error.message; accountMessage.className = 'account-message error'; }
        button.disabled = false;
    });
    deactivateButton?.addEventListener('click', async () => {
        if (!window.confirm('Delete your account? This will sign you out immediately.')) return;
        deactivateButton.disabled = true;
        try {
            await apiRequest('/user', { method: 'DELETE' });
            localStorage.removeItem('buildcost_access_token');
            window.location.href = '/login';
        } catch (error) { accountMessage.textContent = error.message; accountMessage.className = 'account-message error'; deactivateButton.disabled = false; }
    });
};
document.querySelectorAll('.logout-button').forEach((button) => button.addEventListener('click', logout));

if (!token && dashboard) window.location.href = '/login';

const renderUserDashboard = async () => {
    const user = await apiRequest('/user');
    if (user.is_admin) {
        window.location.href = '/admin/dashboard';
        return;
    }
    bindAccountSettings(user);
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
    const regionDistricts = {
        Central: ['Abura/Asebu/Kwamankese', 'Agona East', 'Agona West', 'Ajumako Enyan Essiam', 'Asikuma Odoben Brakwa', 'Assin Central', 'Assin North', 'Assin South', 'Awutu Senya East', 'Awutu Senya West', 'Cape Coast Metropolitan', 'Effutu', 'Ekumfi', 'Gomoa East', 'Gomoa Central', 'Gomoa West', 'Komenda/Edina/Eguafo/Abirem', 'Mfantsiman', 'Twifo Atti-Morkwa', 'Twifo Hemang Lower Denkyira', 'Upper Denkyira East', 'Upper Denkyira West'],
        'Greater Accra': ['Ablekuma Central', 'Ablekuma North', 'Ablekuma West', 'Accra Metropolitan', 'Ada East', 'Ada West', 'Adentan', 'Ashaiman', 'Ayawaso Central', 'Ayawaso East', 'Ayawaso North', 'Ayawaso West', 'Ga Central', 'Ga East', 'Ga North', 'Ga South', 'Ga West', 'Korle Klottey', 'Kpone Katamanso', 'Krowor', 'La Dade-Kotopon', 'La Nkwantanang Madina', 'Ledzokuku', 'Ningo-Prampram', 'Okaikwei North', 'Shai Osudoku', 'Tema Metropolitan', 'Tema West'],
        Ashanti: ['Adansi Asokwa', 'Adansi North', 'Adansi South', 'Afigya Kwabre North', 'Afigya Kwabre South', 'Ahafo Ano North', 'Ahafo Ano South East', 'Ahafo Ano South West', 'Amansie Central', 'Amansie West', 'Amansie South', 'Asante Akim Central', 'Asante Akim North', 'Asante Akim South', 'Asokore Mampong', 'Asokwa', 'Atwima Kwanwoma', 'Atwima Mponua', 'Atwima Nwabiagya North', 'Atwima Nwabiagya South', 'Bekwai Municipal', 'Bosome Freho', 'Bosomtwe', 'Ejisu', 'Ejura-Sekyedumase', 'Kumasi Metropolitan', 'Kwabre East', 'Kwadaso', 'Mampong Municipal', 'Obuasi East', 'Obuasi Municipal', 'Offinso Municipal', 'Offinso North', 'Oforikrom', 'Old Tafo', 'Sekyere Afram Plains', 'Sekyere Central', 'Sekyere East', 'Sekyere Kumawu', 'Sekyere South', 'Suame', 'Suame Municipal', 'Suame North'],
    };
    const regionSelect = form.querySelector('[name="region"]');
    const districtInput = form.querySelector('[name="district"]');
    const districtSelect = document.createElement('select');
    districtSelect.name = 'district';
    districtSelect.required = true;
    districtInput.replaceWith(districtSelect);
    const updateDistricts = () => {
        const districts = regionDistricts[regionSelect.value] || [];
        districtSelect.innerHTML = `<option value="">${districts.length ? 'Select district' : 'Select region first'}</option>`;
        districts.forEach((district) => districtSelect.add(new Option(district, district)));
        districtSelect.disabled = districts.length === 0;
    };
    regionSelect.addEventListener('change', updateDistricts);
    updateDistricts();
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
