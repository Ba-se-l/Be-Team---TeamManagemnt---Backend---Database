/**
 * @fileoverview Child Module: Tasks
 */

async function fetchTasks() {
    if (!ACTIVE_PROJECT_ID) {
        showToast("Please select a project first.", "warning");
        return;
    }
    try {
        const data = await request(`/projects/${ACTIVE_PROJECT_ID}/tasks/?limit=100`, { method: 'GET' });
        const container = document.getElementById('tasks-list');
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<p style="color:var(--clr-text-muted)">No tasks found in this project.</p>';
            return;
        }

        data.forEach(task => {
            const el = document.createElement('div');
            el.className = 'data-item';
            el.innerHTML = `
                <div class="data-info">
                    <h4>${task.title} <span style="font-size:12px; color:var(--clr-primary)">[${task.status}]</span></h4>
                    <p>ID: ${task.id}</p>
                    <p>Priority: ${task.priority}</p>
                    <p>${task.description}</p>
                </div>
            `;
            container.appendChild(el);
        });
        showToast(`Loaded ${data.length} tasks.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function createTask(e) {
    e.preventDefault();
    try {
        const projId = document.getElementById('ctask-proj-id').value;
        const payload = {
            title: document.getElementById('ctask-title').value,
            description: document.getElementById('ctask-desc').value,
            priority: document.getElementById('ctask-priority').value
        };

        const assignee_id = document.getElementById('ctask-assignee').value;
        if (assignee_id && assignee_id.trim() !== '') {
            payload.assignee_to_id = assignee_id.trim();
        }

        await request(`/projects/${projId}/tasks/`, { method: 'POST', body: JSON.stringify(payload) });
        showToast('Task created!', 'success');
        closeModal();
        fetchTasks();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

document.getElementById('btn-trigger-create-task')?.addEventListener('click', () => {
    openModal('tpl-create-task', () => {
        document.getElementById('ctask-proj-id').value = ACTIVE_PROJECT_ID;
    });
});

// Task Dashboard Logic (Inside Project Dashboard)
async function fetchProjectTasks(projectId) {
    try {
        const data = await request(`/projects/${projectId}/tasks/?limit=100`, { method: 'GET' });
        const tbody = document.getElementById('pdv-tasks-table-body');
        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="padding: 16px; text-align: center; color: var(--clr-text-muted);">No tasks found for this project.</td></tr>';
            return;
        }

        // Fetch users to map IDs to Names
        let userMap = {};
        try {
            const users = await request('/users/?limit=100', { method: 'GET' });
            if (users && users.length) {
                users.forEach(u => userMap[u.id] = u.name);
            }
        } catch(e) {
            console.warn("Could not fetch users to map names.");
        }

        data.forEach(task => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = "1px solid var(--clr-border)";
            
            let assigneeName = "Unassigned";
            if (task.assignee_to_id) {
                assigneeName = userMap[task.assignee_to_id] || "Unknown User";
            }
            
            tr.innerHTML = `
                <td style="padding: 12px; font-weight: 500;">
                    ${task.title}
                    <div style="font-size: 11px; color: var(--clr-text-muted); font-weight: normal; margin-top: 4px;">${task.description}</div>
                </td>
                <td style="padding: 12px;">${task.priority.toUpperCase()}</td>
                <td style="padding: 12px;">
                    <span style="background: #e8f0fe; color: var(--clr-primary); padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">
                        ${task.status.replace('_', ' ').toUpperCase()}
                    </span>
                </td>
                <td style="padding: 12px; font-size: 13px;">${assigneeName}</td>
                <td style="padding: 12px; text-align: right;">
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 12px;" onclick="openTaskStatusModal('${task.id}', '${task.status}')">
                        <span class="material-icons-round" style="font-size: 16px;">pending_actions</span> Status
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        showToast(`Loaded ${data.length} project tasks.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function openTaskStatusModal(taskId, currentStatus) {
    openModal('tpl-update-task-status', () => {
        document.getElementById('uptask-id').value = taskId;
        document.getElementById('uptask-status').value = currentStatus;
    });
}

async function updateTaskStatus(e) {
    e.preventDefault();
    try {
        const taskId = document.getElementById('uptask-id').value;
        const payload = {
            status: document.getElementById('uptask-status').value
        };

        // We use the general tasks endpoint to patch
        await request(`/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(payload) });
        showToast('Task status updated!', 'success');
        closeModal();
        if (ACTIVE_PROJECT_ID) {
            fetchProjectTasks(ACTIVE_PROJECT_ID);
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Global Event Listeners
document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-create-task') createTask(e);
    if (e.target && e.target.id === 'form-update-task-status') updateTaskStatus(e);
});

document.getElementById('btn-fetch-tasks')?.addEventListener('click', fetchTasks);
