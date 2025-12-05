import { showToast, apiCall } from '../app.js';
import { initNavbar, logout } from '../auth.js';

// Initialize navbar
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
});

const user = JSON.parse(localStorage.getItem('user') || 'null');

if (!user) {
    window.location.href = 'login.html';
}

const savedJobsContainer = document.getElementById('savedJobsContainer');
const emptyState = document.getElementById('emptyState');

async function loadSavedJobs() {
    try {
        // No user_id needed
        const response = await apiCall(`/api/user/saved-jobs`, 'GET');
        
        if (response.status === 'success' && response.jobs.length > 0) {
            savedJobsContainer.innerHTML = '';
            emptyState.style.display = 'none';
            
            response.jobs.forEach(job => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.padding = '1.5rem';
                
                let matchColorStyle = '';
                const matchScore = job.match_score || 0;
                
                if (matchScore >= 90) matchColorStyle = 'color: #22c55e;';
                else if (matchScore >= 80) matchColorStyle = 'color: #3b82f6;';
                else if (matchScore >= 70) matchColorStyle = 'color: #eab308;';
                else matchColorStyle = 'color: #6b7280;';
                
                card.innerHTML = `
                    <div class="flex flex-col md:flex-row gap-6">
                        <div style="flex: 1;">
                            <div class="flex items-start justify-between mb-3">
                                <div>
                                    <h3 class="text-2xl font-bold mb-2">${job.job_title}</h3>
                                    <p class="text-lg text-muted-foreground font-semibold">${job.company}</p>
                                </div>
                                <div class="text-center">
                                    <div class="text-4xl font-bold" style="${matchColorStyle}">${matchScore}%</div>
                                    <p class="text-xs text-muted-foreground">Match</p>
                                </div>
                            </div>

                            <div class="flex gap-3 mb-4" style="flex-wrap: wrap;">
                                <div class="flex items-center gap-1 text-sm text-muted-foreground">
                                    <i data-lucide="map-pin" style="width: 1rem; height: 1rem;"></i>
                                    ${job.location}
                                </div>
                                <div class="flex items-center gap-1 text-sm text-muted-foreground">
                                    <i data-lucide="globe" style="width: 1rem; height: 1rem;"></i>
                                    ${job.platform || 'Unknown'}
                                </div>
                                <div class="flex items-center gap-1 text-sm text-muted-foreground">
                                    <i data-lucide="calendar" style="width: 1rem; height: 1rem;"></i>
                                    Saved: ${new Date(job.saved_at).toLocaleDateString()}
                                </div>
                            </div>

                            <p class="text-muted-foreground mb-4 leading-relaxed">${job.description}</p>

                            <div class="flex gap-2 mb-4" style="flex-wrap: wrap;">
                                ${(job.skills || []).map(skill => `
                                    <span class="badge" style="background-color: hsl(var(--secondary)); color: hsl(var(--secondary-foreground)); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600;">
                                        ${skill}
                                    </span>
                                `).join('')}
                            </div>

                            ${job.notes ? `<p class="text-sm text-muted-foreground mb-4"><strong>Notes:</strong> ${job.notes}</p>` : ''}

                            <div class="flex gap-2">
                                <a href="${job.url || '#'}" target="_blank" rel="noopener noreferrer" style="display: inline-block; text-decoration: none;">
                                    <button class="btn btn-primary" style="gap: 0.5rem;">
                                        <i data-lucide="external-link" style="width: 1rem; height: 1rem;"></i>
                                        View Job
                                    </button>
                                </a>
                                <button class="btn btn-outline" onclick="removeSavedJob(${job.saved_id})" style="gap: 0.5rem;">
                                    <i data-lucide="trash-2" style="width: 1rem; height: 1rem;"></i>
                                    Remove
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                
                savedJobsContainer.appendChild(card);
            });
            
            lucide.createIcons();
        } else {
            emptyState.style.display = 'block';
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to load saved jobs', 'error');
    }
}

// Make global
window.removeSavedJob = async function(savedId) {
    if (!confirm('Remove this job from saved?')) return;
    
    try {
        // No user_id needed
        const response = await apiCall(`/api/user/saved-job/${savedId}`, 'DELETE');
        
        if (response.status === 'success') {
            showToast('Job removed from saved');
            loadSavedJobs();
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to remove job', 'error');
    }
};

loadSavedJobs();
