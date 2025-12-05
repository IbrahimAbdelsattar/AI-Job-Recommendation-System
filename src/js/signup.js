import { showToast, apiCall } from '../app.js';

const form = document.getElementById('signupForm');
const submitBtn = document.getElementById('submitBtn');
const passwordInput = document.getElementById('password');
const confirmPasswordInput = document.getElementById('confirmPassword');

// Real-time password validation
function validatePasswords() {
    if (confirmPasswordInput.value && passwordInput.value !== confirmPasswordInput.value) {
        confirmPasswordInput.style.borderColor = 'hsl(var(--destructive))';
    } else if (confirmPasswordInput.value) {
        confirmPasswordInput.style.borderColor = 'hsl(var(--primary))';
    } else {
        confirmPasswordInput.style.borderColor = '';
    }
}

passwordInput.addEventListener('input', validatePasswords);
confirmPasswordInput.addEventListener('input', validatePasswords);

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;

    // Validation
    if (!name || !email || !password) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showToast('Passwords do not match', 'error');
        return;
    }
    
    if (password.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }

    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Creating Account...';

    try {
        const response = await apiCall('/api/auth/signup', 'POST', {
            email,
            password,
            full_name: name
        });

        if (response.status === 'success') {
            showToast('Account created successfully!');
            
            // Store user data
            localStorage.setItem('user', JSON.stringify(response.user));
            
            // Redirect to home
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            throw new Error(response.message || 'Failed to sign up');
        }
        
    } catch (error) {
        showToast(error.message || "Failed to sign up", 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign Up';
    }
});
