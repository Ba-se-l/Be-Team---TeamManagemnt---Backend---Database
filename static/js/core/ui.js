/**
 * @fileoverview Parent UI Module
 * Handles DOM manipulation, Toasts, and Modals.
 */

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = document.createElement('span');
    icon.className = 'material-icons-round';
    icon.textContent = type === 'success' ? 'check_circle' : 'error';
    
    const text = document.createElement('span');
    text.textContent = message;

    toast.appendChild(icon);
    toast.appendChild(text);
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideUp 0.3s ease reverse forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function updateAuthStatusUI(isAuthenticated, email = '') {
    const display = document.getElementById('user-email-display');
    const authStatus = document.getElementById('auth-status');
    const btnLogout = document.getElementById('btn-logout');
    
    if (isAuthenticated) {
        display.textContent = email;
        authStatus.style.color = 'var(--clr-primary)';
        if (btnLogout) btnLogout.style.display = 'inline-block';
    } else {
        display.textContent = 'Not Authenticated';
        authStatus.style.color = 'var(--clr-text-muted)';
        if (btnLogout) btnLogout.style.display = 'none';
    }
}

function renderJsonToElement(data, elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = JSON.stringify(data, null, 2);
    }
}

/* =========================================================
   Modal Management
   ========================================================= */

function openModal(templateId, initCallback = null) {
    const overlay = document.getElementById('global-modal-overlay');
    const contentBox = document.getElementById('global-modal-content');
    const tpl = document.getElementById(templateId);
    
    if (!tpl) {
        console.error("Template not found:", templateId);
        return;
    }

    // Clear previous and inject new content
    contentBox.innerHTML = '';
    const clone = tpl.content.cloneNode(true);
    contentBox.appendChild(clone);
    
    overlay.classList.add('active');

    // Run custom initialization if provided (e.g. setting hidden fields)
    if (initCallback) {
        initCallback();
    }
}

function closeModal() {
    const overlay = document.getElementById('global-modal-overlay');
    overlay.classList.remove('active');
}
