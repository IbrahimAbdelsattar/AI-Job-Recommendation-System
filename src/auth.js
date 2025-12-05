// Auth utility functions
export function isLoggedIn() {
    return localStorage.getItem('user') !== null || sessionStorage.getItem('user') !== null;
}

export function getCurrentUser() {
    const user = localStorage.getItem('user') || sessionStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

export async function logout() {
    try {
        await fetch('/api/auth/logout', { 
            method: 'POST',
            credentials: 'include'
        });
    } catch (e) {
        console.error("Logout failed", e);
    }
    localStorage.removeItem('user');
    localStorage.removeItem('jobResults');
    window.location.href = 'login.html';
}

export function initNavbar() {
    const user = getCurrentUser();
    const authButtons = document.getElementById('authButtons');
    const userDropdown = document.getElementById('userDropdown');
    
    if (user && authButtons && userDropdown) {
        // Hide login/signup buttons
        authButtons.style.display = 'none';
        
        // Show user dropdown
        userDropdown.style.display = 'flex';
        
        // Set user info
        const userName = document.getElementById('userName');
        const userPhoto = document.getElementById('userPhoto');
        
        if (userName) {
            userName.textContent = user.full_name || user.email || 'User';
        }
        
        if (userPhoto) {
            if (user.profile_photo) {
                userPhoto.innerHTML = `<img src="${user.profile_photo}" alt="Profile" style="width: 2.5rem; height: 2.5rem; border-radius: 50%; object-fit: cover;">`;
            } else {
                const initials = (user.full_name || user.email || 'U')
                    .split(' ')
                    .map(n => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2);
                userPhoto.innerHTML = `<div style="width: 2.5rem; height: 2.5rem; border-radius: 50%; background: hsl(var(--primary)); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">${initials}</div>`;
            }
        }

        // Dropdown Toggle Logic
        const userMenuBtn = document.getElementById('userMenuBtn');
        const dropdownMenu = document.getElementById('dropdownMenu');
        
        if (userMenuBtn && dropdownMenu) {
            // Remove existing event listeners to avoid duplicates if initNavbar is called multiple times
            const newBtn = userMenuBtn.cloneNode(true);
            userMenuBtn.parentNode.replaceChild(newBtn, userMenuBtn);
            
            newBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = dropdownMenu.style.display === 'block';
                dropdownMenu.style.display = isVisible ? 'none' : 'block';
            });

            // Close dropdown when clicking outside
            document.addEventListener('click', () => {
                dropdownMenu.style.display = 'none';
            });

            // Prevent closing when clicking inside the menu
            dropdownMenu.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }
    }
}

// Initialize navbar on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbar);
} else {
    initNavbar();
}
