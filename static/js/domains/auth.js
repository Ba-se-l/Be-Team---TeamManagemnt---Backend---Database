/**
 * @fileoverview Child Module: Authentication
 * Depends on: api.js, ui.js
 * Handles Login, Registration, and Token Storage logic.
 */

/**
 * Registers a new user.
 * 
 * @param {string} name - User's full name.
 * @param {string} email - User's email.
 * @param {string} password - User's password.
 * @returns {Promise<void>}
 */
async function registerUser(name, email, password) {
    try {
        const payload = {
            name: name,
            email: email,
            password: password,
            job_title: "frontend_developer", // Default testing value
            bio: "Created from Sandbox UI"
        };
        
        await request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        showToast('Registration successful! You can now login.', 'success');
        
        // Auto-fill login email for convenience
        document.getElementById('login-email').value = email;
    } catch (error) {
        showToast(error.message, 'error');
    }
}

/**
 * Logs in the user and stores the JWT in localStorage.
 * 
 * @param {string} email - User's email.
 * @param {string} password - User's password.
 * @returns {Promise<void>}
 */
async function loginUser(email, password) {
    try {
        const payload = { email, password };
        const data = await request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        // Store JWT
        localStorage.setItem('access_token', data.access_token);
        
        // Update UI
        updateAuthStatusUI(true, email);
        showToast('Login successful!', 'success');
        
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

/**
 * Logs out the user by clearing the JWT and updating the UI.
 */
function logoutUser() {
    localStorage.removeItem('access_token');
    updateAuthStatusUI(false);
    showToast('Logged out successfully.', 'success');
    
    // Switch to Auth tab
    const authBtn = document.querySelector('.nav-btn[data-target="auth-view"]');
    if (authBtn) authBtn.click();
}

// ---------------------------------------------------------
// Event Listeners Initialization
// ---------------------------------------------------------
document.getElementById('form-register')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    await registerUser(name, email, password);
});

document.getElementById('form-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    await loginUser(email, password);
});

document.getElementById('btn-logout')?.addEventListener('click', logoutUser);
