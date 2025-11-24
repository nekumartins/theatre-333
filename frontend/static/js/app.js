// Theatre Booking System - Main JavaScript

// Utility functions
const API_BASE = window.location.origin;

async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        return response;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Check authentication status
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

// Logout function
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_id');
    window.location.href = '/login';
}

// Format currency
function formatCurrency(amount) {
    return `$${parseFloat(amount).toFixed(2)}`;
}

// Format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        'bg-blue-500'
    } text-white z-50`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    console.log('Theatre Booking System initialized');
    
    // Update navigation based on auth status
    updateNavigation();
});

function updateNavigation() {
    const token = localStorage.getItem('access_token');
    const email = localStorage.getItem('user_email');
    
    if (token && email) {
        // User is logged in - could update nav to show user info
        console.log('User logged in:', email);
    }
}
