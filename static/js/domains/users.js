/**
 * @fileoverview Child Module: Users
 * Depends on: api.js, ui.js
 */

async function fetchMyProfile() {
    try {
        const data = await request('/users/me', { method: 'GET' });
        renderJsonToElement(data, 'user-profile-json');
        showToast('Profile loaded!', 'success');
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        if (error.message.includes('Not authenticated')) {
            updateAuthStatusUI(false);
            localStorage.removeItem('access_token');
        }
    }
}

async function updateProfile(e) {
    e.preventDefault();
    try {
        const name = document.getElementById('up-name').value;
        const job_title = document.getElementById('up-job').value;
        const bio = document.getElementById('up-bio').value;

        const payload = {};
        if (name) payload.name = name;
        if (job_title) payload.job_title = job_title;
        if (bio) payload.bio = bio;

        await request('/users/me', {
            method: 'PATCH',
            body: JSON.stringify(payload)
        });

        showToast('Profile updated!', 'success');
        closeModal();
        fetchMyProfile();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function changePassword(e) {
    e.preventDefault();
    try {
        const old_password = document.getElementById('cp-old').value;
        const new_password = document.getElementById('cp-new').value;

        await request('/users/me/password', {
            method: 'PATCH',
            body: JSON.stringify({ old_password, new_password })
        });

        showToast('Password changed successfully!', 'success');
        closeModal();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Event Delegation for dynamically injected Modals
document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-update-profile') {
        updateProfile(e);
    }
    if (e.target && e.target.id === 'form-change-password') {
        changePassword(e);
    }
});

document.getElementById('btn-fetch-me')?.addEventListener('click', fetchMyProfile);
