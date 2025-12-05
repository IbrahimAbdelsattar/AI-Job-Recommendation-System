import { showToast, apiCall } from '../app.js';
import { initNavbar, logout, isLoggedIn } from '../auth.js';

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

if (!isLoggedIn()) {
    window.location.href = 'login.html';
}

const textarea = document.getElementById('message');
const charCount = document.getElementById('charCount');
const submitBtn = document.getElementById('submitBtn');
const form = document.getElementById('chatForm');

textarea.addEventListener('input', () => {
    const length = textarea.value.length;
    charCount.textContent = `${length} characters`;
    submitBtn.disabled = length < 50;
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (textarea.value.trim().length < 50) {
        showToast('Please provide more details (at least 50 characters)', 'error');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
    
    try {
        const response = await apiCall('/api/recommend/chat', 'POST', {
            message: textarea.value
        });
        
        if (response.status === 'success') {
            localStorage.setItem('jobResults', JSON.stringify(response.jobs));
            showToast('Analysis complete! Redirecting to results...');
            setTimeout(() => {
                window.location.href = 'results.html';
            }, 1000);
        } else {
            throw new Error(response.message || 'Failed to get recommendations');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to process request", 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Get Job Suggestions';
    }
});
