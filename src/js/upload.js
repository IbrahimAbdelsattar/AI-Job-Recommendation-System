import { showToast, API_URL } from '../app.js';
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

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('cv-upload');
const uploadPrompt = document.getElementById('uploadPrompt');
const fileSelected = document.getElementById('fileSelected');
const fileName = document.getElementById('fileName');
const submitBtn = document.getElementById('submitBtn');
const removeBtn = document.getElementById('removeBtn');
const form = document.getElementById('uploadForm');

let currentFile = null;

// Click to browse
dropZone.addEventListener('click', () => {
    if (!currentFile) {
        fileInput.click();
    }
});

// Drag and drop
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'hsl(var(--primary))';
    dropZone.style.backgroundColor = 'rgba(var(--primary), 0.05)';
});

dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = 'hsl(var(--border))';
    dropZone.style.backgroundColor = 'transparent';
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'hsl(var(--border))';
    dropZone.style.backgroundColor = 'transparent';
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && (droppedFile.type === "application/pdf" || 
        droppedFile.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document")) {
        setFile(droppedFile);
    } else {
        showToast('Please upload a PDF or DOCX file', 'error');
    }
});

// File input change
fileInput.addEventListener('change', (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
        setFile(selectedFile);
    }
});

// Set file
function setFile(file) {
    currentFile = file;
    fileName.textContent = file.name;
    uploadPrompt.style.display = 'none';
    fileSelected.style.display = 'block';
    submitBtn.disabled = false;
    dropZone.style.cursor = 'default';
    lucide.createIcons();
}

// Remove file
removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = '';
    uploadPrompt.style.display = 'block';
    fileSelected.style.display = 'none';
    submitBtn.disabled = true;
    dropZone.style.cursor = 'pointer';
    lucide.createIcons();
});

// Form submit
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentFile) {
        showToast('Please upload your CV', 'error');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
    
    const formData = new FormData();
    formData.append('file', currentFile);
    
    try {
        // Use fetch directly for FormData
        // IMPORTANT: Add credentials: 'include' for session cookie
        const response = await fetch(`${API_URL}/api/recommend/cv`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        });

        if (response.status === 401) {
            showToast('Session expired. Please login again.', 'error');
            setTimeout(() => window.location.href = 'login.html', 1500);
            return;
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            localStorage.setItem('jobResults', JSON.stringify(data.jobs));
            showToast('Analysis complete! Redirecting to results...');
            setTimeout(() => {
                window.location.href = 'results.html';
            }, 1000);
        } else {
            throw new Error(data.message || 'Failed to analyze CV');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || "Failed to process request", 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload and Analyze';
    }
});
