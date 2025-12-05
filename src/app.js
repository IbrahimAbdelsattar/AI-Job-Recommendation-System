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

// API Helper - Simplified and robust
export async function apiCall(endpoint, method = "GET", body = null) {
  const config = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    credentials: 'include',
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    
    // Always get text first
    const text = await response.text();
    
    // Try to parse as JSON
    let data;
    try {
      data = text ? JSON.parse(text) : {};
    } catch (parseError) {
      // Not JSON - likely HTML error page
      console.error('Failed to parse response as JSON:', text.substring(0, 200));
      throw new Error(`Server error (${response.status}): ${response.statusText || 'Invalid response'}`);
    }
    
    // Handle 401 Unauthorized
    if (response.status === 401) {
      showToast('Session expired. Please login again.', 'error');
      setTimeout(() => window.location.href = 'login.html', 1500);
      throw new Error('Unauthorized');
    }
    
    // Handle other errors
    if (!response.ok) {
      throw new Error(data.message || `Request failed (${response.status})`);
    }
    
    return data;
    
  } catch (error) {
    console.error('API Error:', error);
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
