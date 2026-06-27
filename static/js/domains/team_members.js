/**
 * @fileoverview Child Module: Team Members & Dashboard Logic
 */

async function fetchTeamMembers(teamId) {
    try {
        const data = await request(`/teams/${teamId}/members/?limit=100`, { method: 'GET' });
        const tbody = document.getElementById('tdv-members-table-body');
        tbody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="padding: 16px; text-align: center; color: var(--clr-text-muted);">No members found in this team.</td></tr>';
            return;
        }

        // Fetch all users to map IDs to Names (Frontend mapping since backend MemberResponse lacks name)
        let userMap = {};
        try {
            const users = await request('/users/?limit=100', { method: 'GET' });
            if (users && users.length) {
                users.forEach(u => userMap[u.id] = u.name);
            }
        } catch(e) {
            console.warn("Could not fetch users to map names.");
        }

        data.forEach(member => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = "1px solid var(--clr-border)";
            
            // Format joined at date
            const joinedDate = new Date(member.joined_at).toLocaleDateString();
            const memberName = userMap[member.member_id] || "Unknown User";
            
            tr.innerHTML = `
                <td style="padding: 12px; font-family: monospace; font-size: 13px;">${member.member_id}</td>
                <td style="padding: 12px; font-weight: 500;">${memberName}</td>
                <td style="padding: 12px;">
                    <span style="background: #e8f0fe; color: var(--clr-primary); padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: 500;">
                        ${member.role}
                    </span>
                </td>
                <td style="padding: 12px;">${member.is_active ? 'Active' : 'Inactive'}</td>
                <td style="padding: 12px;">${joinedDate}</td>
                <td style="padding: 12px; text-align: right; display: flex; gap: 8px; justify-content: flex-end;">
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 12px;" onclick="openRoleModal('${teamId}', '${member.member_id}', '${member.role}')">
                        <span class="material-icons-round" style="font-size: 16px;">edit</span> Role
                    </button>
                    <button class="btn btn-primary" style="padding: 4px 8px; font-size: 12px;" onclick="openAssignTaskModal('${teamId}', '${member.member_id}')">
                        <span class="material-icons-round" style="font-size: 16px;">assignment_ind</span> Assign Task
                    </button>
                    <button class="btn btn-secondary" style="padding: 4px 8px; font-size: 12px; color: #d32f2f; border-color: #ffcdd2;" onclick="removeTeamMember('${teamId}', '${member.member_id}')">
                        <span class="material-icons-round" style="font-size: 16px; color: #d32f2f;">delete_outline</span> Remove
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        showToast(`Loaded ${data.length} team members.`, 'success');
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function addTeamMember(e) {
    e.preventDefault();
    try {
        const teamId = document.getElementById('cmem-team-id').value;
        const payload = {
            user_id: document.getElementById('cmem-user-id').value,
            role: document.getElementById('cmem-role').value
        };

        await request(`/teams/${teamId}/members/`, { method: 'POST', body: JSON.stringify(payload) });
        showToast('Member added successfully!', 'success');
        closeModal();
        if (ACTIVE_TEAM_ID === teamId) fetchTeamMembers(teamId);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Update Role Logic
function openRoleModal(teamId, userId, currentRole) {
    openModal('tpl-update-member-role', () => {
        document.getElementById('upmem-team-id').value = teamId;
        document.getElementById('upmem-user-id').value = userId;
        document.getElementById('upmem-role').value = currentRole;
    });
}

async function updateMemberRole(e) {
    e.preventDefault();
    try {
        const teamId = document.getElementById('upmem-team-id').value;
        const userId = document.getElementById('upmem-user-id').value;
        const payload = {
            role: document.getElementById('upmem-role').value
        };

        await request(`/teams/${teamId}/members/${userId}`, { method: 'PATCH', body: JSON.stringify(payload) });
        showToast('Role updated successfully!', 'success');
        closeModal();
        if (ACTIVE_TEAM_ID === teamId) fetchTeamMembers(teamId);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Remove Member Logic
async function removeTeamMember(teamId, userId) {
    if (!confirm("Are you sure you want to remove this member from the team?")) return;
    
    try {
        await request(`/teams/${teamId}/members/${userId}`, { method: 'DELETE' });
        showToast('Member removed successfully!', 'success');
        if (ACTIVE_TEAM_ID === teamId) fetchTeamMembers(teamId);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Assign Task Directly Logic
async function openAssignTaskModal(teamId, userId) {
    openModal('tpl-assign-task-to-member', async () => {
        document.getElementById('dtask-assignee').value = userId;
        document.getElementById('dtask-assignee-label').textContent = userId;
        
        // Fetch projects for this team to populate the dropdown
        const select = document.getElementById('dtask-project-id');
        try {
            const projects = await request(`/teams/${teamId}/projects/?limit=100`, { method: 'GET' });
            select.innerHTML = '';
            if (!projects || projects.length === 0) {
                select.innerHTML = '<option value="">No projects available in this team</option>';
            } else {
                projects.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p.id;
                    opt.textContent = p.title;
                    select.appendChild(opt);
                });
            }
        } catch(error) {
            select.innerHTML = '<option value="">Failed to load projects</option>';
        }
    });
}

async function directAssignTask(e) {
    e.preventDefault();
    try {
        const projId = document.getElementById('dtask-project-id').value;
        if (!projId) {
            showToast("You must select a project to assign a task.", "error");
            return;
        }

        const payload = {
            title: document.getElementById('dtask-title').value,
            description: document.getElementById('dtask-desc').value,
            priority: document.getElementById('dtask-priority').value,
            assignee_to_id: document.getElementById('dtask-assignee').value
        };

        await request(`/projects/${projId}/tasks/`, { method: 'POST', body: JSON.stringify(payload) });
        showToast('Task created and assigned successfully!', 'success');
        closeModal();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Global Event Listeners
document.addEventListener('submit', (e) => {
    if (e.target && e.target.id === 'form-add-member') addTeamMember(e);
    if (e.target && e.target.id === 'form-update-member-role') updateMemberRole(e);
    if (e.target && e.target.id === 'form-assign-task') directAssignTask(e);
});
