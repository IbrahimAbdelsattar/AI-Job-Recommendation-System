// Toast Notification
export function showToast(message, type = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  toast.style.display = "block";

  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Backend API URL
// Backend API URL - Empty string for relative paths (same origin)
export const API_URL = "";

// API Helper
export async function apiCall(endpoint, method = "GET", body = null) {
  const headers = {
    "Content-Type": "application/json",
  };

  const config = {
    method,
    headers,
    credentials: 'include',
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    const data = await response.json();

    if (response.status === 401) {
      showToast('Session expired. Please login again.', 'error');
      setTimeout(() => window.location.href = 'login.html', 1500);
      throw new Error('Unauthorized');
    }

    if (!response.ok) {
      throw new Error(data.message || "API Request Failed");
    }

    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

// Navbar Logic (Mobile Toggle if needed, currently simple)
document.addEventListener("DOMContentLoaded", () => {
  // Highlight active link
  const currentPath = window.location.pathname;
  const links = document.querySelectorAll(".nav-link");
  links.forEach((link) => {
    if (link.getAttribute("href") === currentPath.split("/").pop()) {
      link.style.color = "hsl(var(--primary))";
      link.style.fontWeight = "600";
    }
  });
});
