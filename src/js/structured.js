import { showToast, apiCall } from '../app.js';
import { initNavbar, isLoggedIn, getCurrentUser } from '../auth.js';

// Initialize navbar
document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    
    // Setup logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            import('../auth.js').then(module => {
                module.logout();
            });
        });
    }
});

// Check auth on load
if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

const user = getCurrentUser();
if (user && user.email) {
    document.getElementById('email').value = user.email;
}

const form = document.getElementById('structuredForm');
const submitBtn = document.getElementById('submitBtn');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!isLoggedIn()) {
        showToast('You must be logged in', 'error');
        setTimeout(() => window.location.href = 'login.html', 1500);
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Analyzing...';

    const formData = {
        fullName: document.getElementById('fullName').value,
        email: document.getElementById('email').value,
        job_title: document.getElementById('position').value,
        skills: document.getElementById('skills').value.split(',').map(s => s.trim()),
        experience: document.getElementById('experience').value,
        workMode: document.getElementById('workMode').value,
        salary: document.getElementById('salary').value,
        industry: document.getElementById('industry').value,
        location: "Remote", 
        notes: document.getElementById('notes').value
    };

    try {
        const response = await apiCall('/api/recommend/form', 'POST', formData);
        
        if (response.status === 'success') {
            // Ensure jobs are saved
            if (!response.jobs || response.jobs.length === 0) {
                console.warn("No jobs returned from API");
            }
            localStorage.setItem('jobResults', JSON.stringify(response.jobs || []));
            console.log("Jobs saved to localStorage, redirecting...");
            
            showToast('Analysis complete! Redirecting to results...');
            setTimeout(() => {
                // Determine correct path (handle if we are already in src or not)
                const currentPath = window.location.pathname;
                if (currentPath.includes('/src/')) {
                    window.location.href = 'results.html';
                } else {
                    window.location.href = 'src/results.html';
                }
            }, 500);
        } else {
            throw new Error(response.message || 'Failed to get recommendations');
        }

    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to process request", 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Recommendations';
    }
});
