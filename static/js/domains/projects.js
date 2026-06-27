/**
 * @fileoverview Child Module: Projects
 */

let ACTIVE_PROJECT_ID = null;

async function fetchProjects() {
    if (!ACTIVE_TEAM_ID) {
        showToast("Please select a team first.", "warning");
        return;
    }
    try {
        const data = await request(`/teams/${ACTIVE_TEAM_ID}/projects/?limit=100`, { method: 'GET' });
        const container = document.getElementById('projects-list');
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:var(--clr-text-muted)">No projects found in this team.</p>';
            return;
        }

        data.forEach(proj => {
            const el = document.createElement('div');
            el.className = 'data-item';
            el.innerHTML = `
                <div class="data-info">
                    <h4>${proj.title} <span style="font-size:12px; color:var(--clr-primary)">[${proj.status}]</span></h4>
                    <p>ID: ${proj.id}</p>
                    <p>${proj.short_description}</p>
                </div>
                <div class="data-actions">
                    <button class="btn btn-primary" onclick='openProjectDashboard(${JSON.stringify(proj).replace(/'/g, "&#39;")})'>View Dashboard</button>
                </div>
            `;
            container.appendChild(el);
        });
        showToast(`Loaded ${data.length} projects.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function createProject(e) {
    e.preventDefault();
    try {
        const teamId = document.getElementById('cproj-team-id').value;
        const payload = {
            title: document.getElementById('cproj-title').value,
            short_description: document.getElementById('cproj-desc').value
        };
        
        const dl = document.getElementById('cproj-deadline').value;
        if (dl) payload.deadline = new Date(dl).toISOString();

        await request(`/teams/${teamId}/projects/`, { method: 'POST', body: JSON.stringify(payload) });
        showToast('Project created!', 'success');
        closeModal();
        fetchProjects();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function manageTasks(projId) {
    ACTIVE_PROJECT_ID = projId;
    document.getElementById('active-proj-id-display').textContent = projId;
    document.getElementById('btn-trigger-create-task').disabled = false;
    document.getElementById('btn-fetch-tasks').disabled = false;
    
    // Switch to tasks tab visually
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.querySelector('.nav-btn[data-target="tasks-view"]').classList.add('active');
    document.getElementById('tasks-view').classList.add('active');
    
    if (typeof fetchTasks === 'function') fetchTasks();
}

// Project Dashboard Logic
function openProjectDashboard(project) {
    ACTIVE_PROJECT_ID = project.id;
    
    // Populate info
    document.getElementById('pdv-project-title').textContent = project.title + " Dashboard";
    document.getElementById('pdv-desc').textContent = project.short_description || "No description provided.";
    document.getElementById('pdv-status').textContent = project.status.toUpperCase();
    document.getElementById('pdv-deadline').textContent = project.deadline ? new Date(project.deadline).toLocaleString() : "No Deadline";

    // Setup Edit Button
    document.getElementById('btn-pdv-edit-project').onclick = () => {
        openModal('tpl-update-project', () => {
            document.getElementById('upproj-id').value = project.id;
            document.getElementById('upproj-title').value = project.title;
            document.getElementById('upproj-desc').value = project.short_description;
            document.getElementById('upproj-status').value = project.status;
            if (project.deadline) {
                // Slice for datetime-local format
                document.getElementById('upproj-deadline').value = new Date(project.deadline).toISOString().slice(0, 16);
            } else {
                document.getElementById('upproj-deadline').value = "";
            }
        });
    };

    // Setup Create Task Button inside Dashboard
    document.getElementById('btn-pdv-create-task').onclick = () => {
        openModal('tpl-create-task', () => {
            document.getElementById('ctask-proj-id').value = project.id;
        });
    };

    // Setup Refresh Tasks
    document.getElementById('btn-pdv-refresh-tasks').onclick = () => {
        if (typeof fetchProjectTasks === 'function') fetchProjectTasks(project.id);
    };

    // Switch View
    document.querySelectorAll('.view-section').forEach(v => v.classList.remove('active'));
    document.getElementById('project-details-view').classList.add('active');

    // Fetch Tasks
    if (typeof fetchProjectTasks === 'function') fetchProjectTasks(project.id);
}

async function updateProject(e) {
    e.preventDefault();
    try {
        const projId = document.getElementById('upproj-id').value;
        const payload = {
            title: document.getElementById('upproj-title').value,
            short_description: document.getElementById('upproj-desc').value,
            status: document.getElementById('upproj-status').value
        };
        const dl = document.getElementById('upproj-deadline').value;
        if (dl) {
            payload.deadline = new Date(dl).toISOString();
        }

        // We use the general project endpoint to patch
        await request(`/projects/${projId}`, { method: 'PATCH', body: JSON.stringify(payload) });
        showToast('Project updated successfully!', 'success');
        closeModal();
        
        // Refresh the whole projects list
        fetchProjects();
        // The dashboard data will update when we reopen it or we just exit out.
        // Easiest is to bounce back to projects view or trigger a re-render.
        document.querySelector('.nav-btn[data-target="projects-view"]').click();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Wire up the dynamic creation modal
document.getElementById('btn-trigger-create-project')?.addEventListener('click', () => {
    openModal('tpl-create-project', () => {
        document.getElementById('cproj-team-id').value = ACTIVE_TEAM_ID;
    });
});

document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-create-project') createProject(e);
    if (e.target && e.target.id === 'form-update-project') updateProject(e);
});

document.getElementById('btn-fetch-projects')?.addEventListener('click', fetchProjects);
