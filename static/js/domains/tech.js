/**
 * @fileoverview Child Module: Technology
 * Depends on: api.js, ui.js
 */

async function fetchTechnologies() {
    try {
        const data = await request('/technologies/', { method: 'GET' });
        const container = document.getElementById('tech-list');
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:var(--clr-text-muted)">No technologies found.</p>';
            return;
        }

        data.forEach(tech => {
            const el = document.createElement('div');
            el.className = 'data-item';
            el.innerHTML = `
                <div class="data-info">
                    <h4>${tech.name}</h4>
                    <p>ID: ${tech.id}</p>
                    <p>${tech.description || 'No description'}</p>
                    <p>Docs: <a href="${tech.documentation_url || '#'}" target="_blank">Link</a></p>
                </div>
            `;
            container.appendChild(el);
        });
        showToast(`Loaded ${data.length} technologies.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function createTechnology(e) {
    e.preventDefault();
    try {
        const payload = {
            name: document.getElementById('ctech-name').value,
            description: document.getElementById('ctech-desc').value || undefined,
            documentation_url: document.getElementById('ctech-url').value || undefined
        };

        await request('/technologies/', {
            method: 'POST',
            body: JSON.stringify(payload)
        });

        showToast('Technology created!', 'success');
        closeModal();
        fetchTechnologies();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-create-tech') {
        createTechnology(e);
    }
});

document.getElementById('btn-fetch-tech')?.addEventListener('click', fetchTechnologies);
