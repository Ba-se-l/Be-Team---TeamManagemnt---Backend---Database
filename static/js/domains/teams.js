/**
 * @fileoverview Child Module: Teams
 */

// Global state for hierarchical drill-down
let ACTIVE_TEAM_ID = null;

async function fetchTeams() {
    try {
        const data = await request('/teams/?limit=100&offset=0', { method: 'GET' });
        const container = document.getElementById('teams-list');
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:var(--clr-text-muted)">No teams found.</p>';
            return;
        }

        data.forEach(team => {
            const el = document.createElement('div');
            el.className = 'data-item';
            el.innerHTML = `
                <div class="data-info">
                    <h4>${team.name}</h4>
                    <p>ID: ${team.id}</p>
                    <p>${team.description || 'No description'}</p>
                    <p>Active: ${team.is_active}</p>
                </div>
                <div class="data-actions">
                    <button class="btn btn-primary" onclick="openTeamDashboard('${team.id}', '${team.name}')">View Dashboard</button>
                </div>
            `;
            container.appendChild(el);
        });
        showToast(`Loaded ${data.length} teams.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function createTeam(e) {
    e.preventDefault();
    try {
        const payload = {
            name: document.getElementById('ct-name').value,
            description: document.getElementById('ct-desc').value || undefined
        };
        await request('/teams/', { method: 'POST', body: JSON.stringify(payload) });
        showToast('Team created!', 'success');
        closeModal();
        fetchTeams();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function manageProjects(teamId) {
    ACTIVE_TEAM_ID = teamId;
    document.getElementById('active-team-id-display').textContent = teamId;
    document.getElementById('btn-trigger-create-project').disabled = false;
    document.getElementById('btn-fetch-projects').disabled = false;
    
    // Switch to projects tab visually
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.querySelector('.nav-btn[data-target="projects-view"]').classList.add('active');
    document.getElementById('projects-view').classList.add('active');
    
    if (typeof fetchProjects === 'function') fetchProjects();
}

// Dashboard Navigation
function openTeamDashboard(teamId, teamName) {
    ACTIVE_TEAM_ID = teamId;
    
    // Update Dashboard UI
    document.getElementById('tdv-team-name').textContent = teamName + " Dashboard";
    
    // Set up "Add Member" button inside dashboard
    const btnAddMember = document.getElementById('btn-tdv-add-member');
    btnAddMember.onclick = () => {
        openModal('tpl-add-member', () => {
            document.getElementById('cmem-team-id').value = teamId;
        });
    };

    // Set up refresh button
    const btnRefresh = document.getElementById('btn-tdv-refresh-members');
    btnRefresh.onclick = () => {
        if (typeof fetchTeamMembers === 'function') fetchTeamMembers(teamId);
    };

    // Set up Manage Projects button
    const btnManageProjects = document.getElementById('btn-tdv-manage-projects');
    if (btnManageProjects) {
        btnManageProjects.onclick = () => {
            manageProjects(teamId);
        };
    }

    // Switch view
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.getElementById('team-details-view').classList.add('active');

    // Fetch members
    if (typeof fetchTeamMembers === 'function') {
        fetchTeamMembers(teamId);
    }
}

document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-create-team') createTeam(e);
});

document.getElementById('btn-fetch-teams')?.addEventListener('click', fetchTeams);
