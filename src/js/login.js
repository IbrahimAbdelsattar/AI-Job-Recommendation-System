import { showToast, apiCall } from "../app.js";

const form = document.getElementById("loginForm");
const submitBtn = document.getElementById("submitBtn");
const emailInput = document.getElementById("email");
const rememberCheckbox = document.getElementById("remember");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = emailInput.value;
  const password = document.getElementById("password").value;
  const rememberMe = rememberCheckbox.checked;

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> Logging in...';

  try {
    const response = await apiCall('/api/auth/login', 'POST', { email, password });
    if (response.status === 'success') {
      if (rememberMe) {
        localStorage.setItem('user', JSON.stringify(response.user));
      } else {
        sessionStorage.setItem('user', JSON.stringify(response.user));
        // Also store in localStorage for initNavbar fallback
        localStorage.setItem('user', JSON.stringify(response.user));
      }
      showToast('Login successful!');
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
