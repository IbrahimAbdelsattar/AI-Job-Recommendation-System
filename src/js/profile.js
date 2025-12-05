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

const profilePhotoDisplay = document.getElementById('profilePhotoDisplay');
const photoInput = document.getElementById('photoInput');

// Load profile data
async function loadProfile() {
    try {
        // No user_id param needed, session used
        const response = await apiCall(`/api/user/profile`, 'GET');
        
        if (response.status === 'success') {
            document.getElementById('fullName').value = response.user.full_name || '';
            document.getElementById('email').value = response.user.email || '';
            
            // Update localStorage with latest data
            const currentUser = JSON.parse(localStorage.getItem('user'));
            if (currentUser) {
                currentUser.full_name = response.user.full_name;
                currentUser.email = response.user.email;
                currentUser.profile_photo = response.user.profile_photo;
                localStorage.setItem('user', JSON.stringify(currentUser));
                
                // Update navbar image immediately if possible
                const userPhoto = document.getElementById('userPhoto');
                if (userPhoto && response.user.profile_photo) {
                        userPhoto.innerHTML = `<img src="${response.user.profile_photo}" alt="Profile" style="width: 2.5rem; height: 2.5rem; border-radius: 50%; object-fit: cover;">`;
                }
            }
            
            // Display profile photo
            if (response.user.profile_photo) {
                profilePhotoDisplay.innerHTML = `<img src="${response.user.profile_photo}" alt="Profile" class="profile-photo">`;
            } else {
                // Show initials if no photo
                const initials = (response.user.full_name || response.user.email || 'U')
                    .split(' ')
                    .map(n => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2);
                profilePhotoDisplay.innerHTML = `<div class="profile-photo" style="font-size: 3rem; font-weight: bold;">${initials}</div>`;
            }
            lucide.createIcons();
        }
    } catch (error) {
        console.error(error);
        showToast('Failed to load profile', 'error');
    }
}

// Photo upload with Cropper
let cropper = null;
const cropperModal = document.getElementById('cropperModal');
const cropperImage = document.getElementById('cropperImage');
const cancelCropBtn = document.getElementById('cancelCropBtn');
const cropBtn = document.getElementById('cropBtn');

photoInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showToast('File size must be less than 5MB', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        cropperImage.src = e.target.result;
        cropperModal.style.display = 'flex';
        
        if (cropper) {
            cropper.destroy();
        }
        
        cropper = new Cropper(cropperImage, {
            aspectRatio: 1,
            viewMode: 1,
            autoCropArea: 1,
        });
    };
    reader.readAsDataURL(file);
    
    // Reset input value so same file can be selected again if cancelled
    e.target.value = '';
});

cancelCropBtn.addEventListener('click', () => {
    cropperModal.style.display = 'none';
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

cropBtn.addEventListener('click', async () => {
    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas({
        width: 300,
        height: 300,
    });

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('photo', blob, 'profile.jpg');
        // No user_id needed

        cropBtn.disabled = true;
        cropBtn.innerHTML = '<span class="spinner"></span> Uploading...';

        try {
            // Use fetch directly for FormData, include credentials
            const response = await fetch('http://localhost:5000/api/user/upload-photo', {
                method: 'POST',
                body: formData,
                credentials: 'include'
            });

            const data = await response.json();

            if (data.status === 'success') {
                showToast('Profile photo updated!');
                // Update user in localStorage
                user.profile_photo = data.photo_url;
                localStorage.setItem('user', JSON.stringify(user));
                
                // Update display
                profilePhotoDisplay.innerHTML = `<img src="${data.photo_url}" alt="Profile" class="profile-photo">`;
                
                // Close modal
                cropperModal.style.display = 'none';
                if (cropper) {
                    cropper.destroy();
                    cropper = null;
                }
            } else {
                throw new Error(data.message || 'Failed to upload photo');
            }
        } catch (error) {
            console.error(error);
            showToast(error.message || 'Failed to upload photo', 'error');
        } finally {
            cropBtn.disabled = false;
            cropBtn.textContent = 'Save Photo';
        }
    }, 'image/jpeg');
});

// Update profile
const profileForm = document.getElementById('profileForm');
const updateProfileBtn = document.getElementById('updateProfileBtn');

profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    updateProfileBtn.disabled = true;
    updateProfileBtn.innerHTML = '<span class="spinner"></span> Updating...';
    
    try {
        const response = await apiCall('/api/user/profile', 'PUT', {
            // No user_id needed
            full_name: document.getElementById('fullName').value,
            email: document.getElementById('email').value
        });
        
        if (response.status === 'success') {
            // Update localStorage
            user.full_name = document.getElementById('fullName').value;
            user.email = document.getElementById('email').value;
            localStorage.setItem('user', JSON.stringify(user));
            
            showToast('Profile updated successfully!');
            loadProfile(); // Reload to update initials if needed
        } else {
            throw new Error(response.message || 'Failed to update profile');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Failed to update profile', 'error');
    } finally {
        updateProfileBtn.disabled = false;
        updateProfileBtn.textContent = 'Update Profile';
    }
});

// Change password
const passwordForm = document.getElementById('passwordForm');
const changePasswordBtn = document.getElementById('changePasswordBtn');

passwordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    
    if (newPassword !== confirmNewPassword) {
        showToast('New passwords do not match', 'error');
        return;
    }
    
    if (newPassword.length < 8) {
        showToast('Password must be at least 8 characters', 'error');
        return;
    }
    
    changePasswordBtn.disabled = true;
    changePasswordBtn.innerHTML = '<span class="spinner"></span> Changing...';
    
    try {
        const response = await apiCall('/api/user/change-password', 'POST', {
            // No user_id needed
            current_password: currentPassword,
            new_password: newPassword
        });
        
        if (response.status === 'success') {
            showToast('Password changed successfully!');
            passwordForm.reset();
        } else {
            throw new Error(response.message || 'Failed to change password');
        }
    } catch (error) {
        console.error(error);
        showToast(error.message || 'Failed to change password', 'error');
    } finally {
        changePasswordBtn.disabled = false;
        changePasswordBtn.textContent = 'Change Password';
    }
});

loadProfile();
