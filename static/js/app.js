/**
 * @fileoverview Main Application Entry Point
 * Handles Tab Navigation and Initial Boot Logic.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Check Initial Auth Status
    const token = localStorage.getItem('access_token');
    if (token) {
        // We have a token, we don't know the email unless we fetch /me
        updateAuthStatusUI(true, 'Session Active');
        
        // Auto-switch to Teams tab if already logged in to save time
        const teamsBtn = document.querySelector('.nav-btn[data-target="teams-view"]');
        if (teamsBtn) teamsBtn.click();
        
        // Optionally pre-fetch user profile here
        if (typeof fetchMyProfile === 'function') fetchMyProfile().catch(() => {});
        if (typeof fetchTeams === 'function') fetchTeams();
    } else {
        updateAuthStatusUI(false);
    }

    // 2. Setup Tab Navigation
    const navButtons = document.querySelectorAll('.nav-btn');
    const viewSections = document.querySelectorAll('.view-section');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all buttons and sections
            navButtons.forEach(b => b.classList.remove('active'));
            viewSections.forEach(v => v.classList.remove('active'));

            // Add active class to clicked button and target section
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
});
