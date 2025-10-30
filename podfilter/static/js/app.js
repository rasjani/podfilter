// Common JavaScript functions for PodFilter

// Authentication helper
function getAuthToken() {
    return localStorage.getItem('access_token');
}

function setAuthToken(token) {
    localStorage.setItem('access_token', token);
}

function removeAuthToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return !!getAuthToken();
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Authorization': 'Bearer ' + getAuthToken()
            },
            credentials: 'same-origin'
        });
        if (!response.ok) {
            console.warn('Logout request failed with status', response.status);
        }

        removeAuthToken();
        localStorage.removeItem('podfilter.selectedFeed');
        window.location.replace('/');
    } catch (error) {
        console.error('Logout error:', error);
        removeAuthToken();
        localStorage.removeItem('podfilter.selectedFeed');
        window.location.replace('/');
    }
}

// Show loading spinner
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    element.disabled = true;
    return originalContent;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// API request helper with authentication
async function apiRequest(url, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers,
        credentials: options.credentials || 'same-origin'
    });
    
    if (response.status === 401) {
        removeAuthToken();
        window.location.href = '/login';
        return;
    }
    
    return response;
}

// Form validation helper
function validateForm(formElement) {
    const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Copy to clipboard helper
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showAlert('Copied to clipboard!', 'success');
    } catch (error) {
        console.error('Failed to copy to clipboard:', error);
        showAlert('Failed to copy to clipboard', 'error');
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status and update UI
    if (isAuthenticated()) {
        // Add auth token to all API requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (url.startsWith('/') && !url.startsWith('/static/')) {
                const token = getAuthToken();
                if (token) {
                    options.headers = {
                        ...options.headers,
                        'Authorization': 'Bearer ' + token
                    };
                }
                options.credentials = options.credentials || 'same-origin';
            }
            return originalFetch(url, options);
        };
    }
    
    // Add click handlers for common actions
    document.addEventListener('click', function(e) {
        // Handle copy RSS URL buttons
        if (e.target.classList.contains('copy-rss-url')) {
            e.preventDefault();
            const url = e.target.getAttribute('data-url');
            copyToClipboard(url);
        }
    });
    
    // Add form validation
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (form.classList.contains('needs-validation')) {
            if (!validateForm(form)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });
});
