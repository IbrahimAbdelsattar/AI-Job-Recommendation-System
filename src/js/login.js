import { showToast, apiCall } from "../app.js";

const form = document.getElementById("loginForm");
const submitBtn = document.getElementById("submitBtn");
const emailInput = document.getElementById("email");
const rememberCheckbox = document.getElementById("remember");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  
  const email = emailInput.value.trim();
  const password = document.getElementById("password").value;
  const rememberMe = rememberCheckbox.checked;

  // Validation
  if (!email || !password) {
    showToast('Please fill in all fields', 'error');
    return;
  }

  // Disable button and show loading
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Logging in...';

  try {
    const response = await apiCall('/api/auth/login', 'POST', { email, password });
    
    if (response.status === 'success') {
      // Store user data
      localStorage.setItem('user', JSON.stringify(response.user));
      
      showToast('Login successful!');
      
      // Redirect to home
      setTimeout(() => {
        window.location.href = 'index.html';
      }, 1000);
    } else {
      throw new Error(response.message || 'Failed to login');
    }
    
  } catch (error) {
    showToast(error.message || 'Failed to login', 'error');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Login';
  }
});
