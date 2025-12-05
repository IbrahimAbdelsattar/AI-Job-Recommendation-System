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

const historyContainer = document.getElementById('historyContainer');
const emptyState = document.getElementById('emptyState');

async function loadHistory() {
    try {
        // No user_id needed
        const response = await apiCall(`/api/user/searches`, 'GET');
        
        if (response.status === 'success' && response.searches.length > 0) {
            historyContainer.innerHTML = '';
            emptyState.style.display = 'none';
            
            response.searches.forEach(search => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.padding = '1.5rem';
                
                const date = new Date(search.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const typeIcons = {
                    'form': 'file-text',
                    'chat': 'message-square',
                    'cv': 'upload'
                };
                
                card.innerHTML = `
                    <div class="flex items-start justify-between">
                        <div style="flex: 1;">
                            <div class="flex items-center gap-2 mb-2">
                                <i data-lucide="${typeIcons[search.search_type] || 'search'}" style="width: 1.25rem; height: 1.25rem;" class="text-primary"></i>
                                <span class="font-semibold" style="text-transform: capitalize;">${search.search_type} Search</span>
                            </div>
                            <p class="text-muted-foreground mb-2"><strong>Keywords:</strong> ${search.keywords || 'N/A'}</p>
                            <p class="text-sm text-muted-foreground">${date}</p>
                        </div>
                        <button class="btn btn-primary" onclick="viewResults(${search.id})">
                            View Results
                        </button>
                    </div>
                `;
                
                historyContainer.appendChild(card);
            });
            
            lucide.createIcons();
        } else {
            emptyState.style.display = 'block';
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to load history', 'error');
    }
}

// Make viewResults global so onclick works
window.viewResults = async function(searchId) {
    try {
        const response = await apiCall(`/api/search/${searchId}/results`, 'GET');
        
        if (response.status === 'success') {
            localStorage.setItem('jobResults', JSON.stringify(response.jobs));
            window.location.href = 'results.html';
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to load results', 'error');
    }
};

loadHistory();
