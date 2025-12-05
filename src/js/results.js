import { showToast, apiCall, API_URL } from '../app.js';
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
const storedJobs = localStorage.getItem('jobResults');
let jobs = [];

if (storedJobs) {
    try {
        jobs = JSON.parse(storedJobs);
    } catch (e) {
        console.error("Failed to parse jobs", e);
    }
}

if (jobs.length === 0) {
    document.getElementById('jobsContainer').innerHTML = `
        <div class="text-center py-12">
            <p class="text-muted-foreground text-lg">No recommendations found. Please submit a search first.</p>
            <a href="structured.html" class="btn btn-primary mt-4">Go to Search</a>
        </div>
    `;
}

const container = document.getElementById('jobsContainer');
document.getElementById('jobCount').textContent = jobs.length;

jobs.forEach(job => {
    const card = document.createElement('div');
    card.className = 'card hover:shadow-lg transition-all duration-300';
    card.style.padding = '1.5rem';
    
    let matchColorStyle = '';
    const matchScore = job.match_score || job.match || 0;
    
    if (matchScore >= 90) matchColorStyle = 'color: #22c55e;';
    else if (matchScore >= 80) matchColorStyle = 'color: #3b82f6;';
    else if (matchScore >= 70) matchColorStyle = 'color: #eab308;';
    else matchColorStyle = 'color: #6b7280;';

    card.innerHTML = `
        <div class="flex flex-col md:flex-row gap-6">
            <div style="flex: 1;">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <h3 class="text-2xl font-bold mb-2">${job.title}</h3>
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
                        <i data-lucide="dollar-sign" style="width: 1rem; height: 1rem;"></i>
                        ${job.salary || 'Not specified'}
                    </div>
                    <div class="flex items-center gap-1 text-sm text-muted-foreground">
                        <i data-lucide="globe" style="width: 1rem; height: 1rem;"></i>
                        ${job.platform || 'Unknown'}
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

                <div class="flex gap-2">
                    <a href="${job.url || job.linkedin || '#'}" target="_blank" rel="noopener noreferrer" style="display: inline-block; text-decoration: none;">
                        <button class="btn btn-primary" style="gap: 0.5rem;">
                            <i data-lucide="briefcase" style="width: 1rem; height: 1rem;"></i>
                            View Job
                            <i data-lucide="external-link" style="width: 1rem; height: 1rem;"></i>
                        </button>
                    </a>
                    ${user ? `
                        <button class="btn btn-outline" onclick="saveJob(${job.id})" style="gap: 0.5rem;">
                            <i data-lucide="bookmark" style="width: 1rem; height: 1rem;"></i>
                            Save Job
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    container.appendChild(card);
});

lucide.createIcons();

// Save job function
window.saveJob = async function(jobId) {
    if (!user) {
        showToast('Please login to save jobs', 'error');
        return;
    }

    try {
        // No user_id needed
        const response = await apiCall('/api/user/save-job', 'POST', {
            job_result_id: jobId
        });

        if (response.status === 'success') {
            showToast('Job saved successfully!');
        } else {
            throw new Error(response.message || 'Failed to save job');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Failed to save job', 'error');
    }
};

// Export PDF function
const exportPdfBtn = document.getElementById('exportPdfBtn');
if (exportPdfBtn) {
    exportPdfBtn.addEventListener('click', async () => {
        exportPdfBtn.disabled = true;
        exportPdfBtn.innerHTML = '<span class="spinner"></span> Generating...';

        try {
            const response = await fetch(`${API_URL}/api/export/pdf`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    jobs: jobs,
                    user_name: user ? user.full_name || user.email : 'User'
                })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `job_recommendations_${new Date().toISOString().split('T')[0]}.pdf`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                showToast('PDF downloaded successfully!');
            } else {
                throw new Error('Failed to generate PDF');
            }
        } catch (error) {
            console.error(error);
            showToast('Failed to export PDF', 'error');
        } finally {
            exportPdfBtn.disabled = false;
            exportPdfBtn.innerHTML = '<i data-lucide="download" style="width: 1rem; height: 1rem;"></i> Export to PDF';
            lucide.createIcons();
        }
    });
}
