const dashboard = document.querySelector('[data-dashboard="admin"]');
const resource = dashboard?.dataset.resource;
const token = localStorage.getItem('buildcost_access_token');
const message = document.querySelector('.dashboard-message');

const resourceConfig = {
    materials: { singular: 'material', endpoint: '/admin/materials', columns: [['item', 'Item'], ['region', 'Region'], ['district', 'District'], ['unit', 'Unit'], ['price', 'Price'], ['source', 'Source']], fields: [{ name: 'region', label: 'Region', type: 'select', options: ['Central', 'Greater Accra', 'Ashanti'] }, { name: 'district', label: 'District' }, { name: 'item', label: 'Item', type: 'select', options: ['Cement', 'Sand', 'Stones', 'Iron Rods', 'Wood', 'Tiles', 'Paint', 'Plumbing Materials', 'Electrical Materials'] }, { name: 'unit', label: 'Unit', placeholder: 'e.g. bag, tonne, m²' }, { name: 'price', label: 'Price (GH₵)', type: 'number', step: '0.01' }, { name: 'source', label: 'Source' }] },
    permits: { singular: 'permit', endpoint: '/admin/permits', columns: [['fee_type', 'Fee type'], ['region', 'Region'], ['district', 'District'], ['amount', 'Amount'], ['source', 'Source']], fields: [{ name: 'region', label: 'Region', type: 'select', options: ['Central', 'Greater Accra', 'Ashanti'] }, { name: 'district', label: 'District' }, { name: 'fee_type', label: 'Fee type' }, { name: 'amount', label: 'Amount (GH₵)', type: 'number', step: '0.01' }, { name: 'source', label: 'Source' }] },
    land_prices: { singular: 'land price', endpoint: '/admin/land_prices', columns: [['region', 'Region'], ['district', 'District'], ['price', 'Price'], ['source', 'Source']], fields: [{ name: 'region', label: 'Region', type: 'select', options: ['Central', 'Greater Accra', 'Ashanti'] }, { name: 'district', label: 'District' }, { name: 'price', label: 'Price (GH₵)', type: 'number', step: '0.01' }, { name: 'source', label: 'Source' }] },
    labor_rates: { singular: 'labour rate', endpoint: '/admin/labor_rates', columns: [['trade', 'Trade'], ['region', 'Region'], ['district', 'District'], ['rate', 'Rate'], ['source', 'Source']], fields: [{ name: 'region', label: 'Region', type: 'select', options: ['Central', 'Greater Accra', 'Ashanti'] }, { name: 'district', label: 'District' }, { name: 'trade', label: 'Trade' }, { name: 'rate', label: 'Rate (GH₵)', type: 'number', step: '0.01' }, { name: 'source', label: 'Source' }] },
};

const config = resourceConfig[resource];
let referenceRegions = {};
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
}[character]));
const request = async (path, options = {}) => {
    const response = await fetch(path, { ...options, headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, ...(options.headers || {}) } });
    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch { data = { detail: text || 'Request failed.' }; }
    if (!response.ok) throw new Error(data.detail || 'Unable to complete that request.');
    return data;
};
const showMessage = (text, error = false) => { message.textContent = text; message.className = `dashboard-message${error ? ' error' : ' success'}`; };
const formPanel = document.querySelector('[data-form-panel]');
const form = document.querySelector('[data-resource-form]');
let editingId = null;

const renderForm = (record = {}) => {
    form.innerHTML = config.fields.map((field) => {
        const value = record[field.name] ?? '';
        const input = field.name === 'district'
            ? `<select name="district" required><option value="">Select district</option>${(referenceRegions[record.region] || []).map((district) => `<option ${district === value ? 'selected' : ''}>${escapeHtml(district)}</option>`).join('')}</select>`
            : field.type === 'select'
            ? `<select name="${field.name}" required><option value="">Select ${field.label.toLowerCase()}</option>${field.options.map((option) => `<option ${option === value ? 'selected' : ''}>${option}</option>`).join('')}</select>`
            : `<input name="${field.name}" type="${field.type || 'text'}" ${field.step ? `step="${field.step}"` : ''} value="${escapeHtml(value)}" required placeholder="${escapeHtml(field.placeholder || '')}">`;
        return `<label>${field.label}${input}</label>`;
    }).join('') + '<button class="button form-button" type="submit"><span data-submit-label>Save record</span><span aria-hidden="true">&#8594;</span></button>';
    document.querySelector('[data-form-title]').textContent = editingId ? `Edit ${config.singular}` : `Add ${config.singular}`;
    formPanel.hidden = false;
    form.querySelector('[name="region"]')?.addEventListener('change', (event) => {
        const districtSelect = form.querySelector('[name="district"]');
        districtSelect.innerHTML = '<option value="">Select district</option>';
        (referenceRegions[event.target.value] || []).forEach((district) => districtSelect.add(new Option(district, district)));
        districtSelect.disabled = !(referenceRegions[event.target.value] || []).length;
    });
    form.querySelector('input, select')?.focus();
};

const renderRecords = (records) => {
    document.querySelector('[data-record-count]').textContent = `${records.length} record${records.length === 1 ? '' : 's'}`;
    document.querySelector('[data-table-head]').innerHTML = config.columns.map(([, label]) => `<th>${label}</th>`).join('') + '<th>Actions</th>';
    document.querySelector('[data-record-list]').innerHTML = records.length ? records.map((record) => `<tr>${config.columns.map(([key]) => `<td>${escapeHtml(record[key] ?? '-')}</td>`).join('')}<td class="table-actions"><button type="button" data-edit="${record.id}">Edit</button><button type="button" data-delete="${record.id}">Delete</button></td></tr>`).join('') : `<tr><td colspan="${config.columns.length + 1}" class="empty-state">No records yet. Add the first one above.</td></tr>`;
    document.querySelectorAll('[data-edit]').forEach((button) => button.addEventListener('click', () => loadRecord(button.dataset.edit)));
    document.querySelectorAll('[data-delete]').forEach((button) => button.addEventListener('click', () => deleteRecord(button.dataset.delete)));
};

const loadRecords = async () => renderRecords(await request(config.endpoint));
const loadRecord = async (id) => { editingId = id; renderForm(await request(`${config.endpoint}/${id}`)); };
const deleteRecord = async (id) => { if (!window.confirm('Delete this record?')) return; try { await request(`${config.endpoint}/${id}`, { method: 'DELETE' }); showMessage('Record deleted.'); await loadRecords(); } catch (error) { showMessage(error.message, true); } };

form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const payload = Object.fromEntries(new FormData(form));
    ['price', 'amount', 'rate'].forEach((key) => { if (payload[key]) payload[key] = Number(payload[key]); });
    try { await request(editingId ? `${config.endpoint}/${editingId}` : config.endpoint, { method: editingId ? 'PUT' : 'POST', body: JSON.stringify(payload) }); showMessage(`${config.singular[0].toUpperCase() + config.singular.slice(1)} saved.`); formPanel.hidden = true; editingId = null; await loadRecords(); } catch (error) { showMessage(error.message, true); }
});
document.querySelector('[data-add-record]').addEventListener('click', () => { editingId = null; renderForm(); });
document.querySelector('[data-cancel-form]').addEventListener('click', () => { formPanel.hidden = true; editingId = null; });

document.querySelectorAll('.logout-button').forEach((button) => button.addEventListener('click', async () => { try { await fetch('/logout', { method: 'POST', headers: { Authorization: `Bearer ${token}` } }); } finally { localStorage.removeItem('buildcost_access_token'); window.location.href = '/login'; } }));
if (token && config) request('/reference/regions').then((regions) => { referenceRegions = regions; return loadRecords(); }).catch((error) => showMessage(error.message, true));
