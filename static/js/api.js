// GEC Rajkot Utilities
window.GECUtils = window.GECUtils || {};

// API Helper
GECUtils.API = {
    post: function(path, body) {
        return fetch(path, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) })
            .then(r => r.json().then(j => ({ ok: r.ok, status: r.status, body: j })))
    }
};

// Loading Manager
GECUtils.LoadingManager = {
    setLoading: function(button, isLoading) {
        if (!button) return;
        
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }
};

// Toast Notifications
GECUtils.toast = {
    success: function(message) {
        this.show(message, 'success');
    },
    error: function(message) {
        this.show(message, 'error');
    },
    info: function(message) {
        this.show(message, 'info');
    },
    show: function(message, type) {
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
            document.body.appendChild(container);
        }

        // Create toast element
        const toast = document.createElement('div');
        const bgColor = type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6';
        toast.style.cssText = `
            background: ${bgColor};
            color: white;
            padding: 16px 24px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.3s ease-out;
            min-width: 250px;
            max-width: 400px;
        `;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};

// Form Validator
GECUtils.FormValidator = class {
    constructor(form) {
        this.form = form;
    }

    showError(fieldName, message) {
        const field = this.form.querySelector(`[name="${fieldName}"], #${fieldName}`);
        if (!field) return;

        field.classList.add('border-red-500');
        field.classList.remove('border-green-500');

        // Remove existing error message
        const existingError = field.parentElement.querySelector('.error-message');
        if (existingError) existingError.remove();

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message text-red-600 text-sm mt-1';
        errorDiv.textContent = message;
        field.parentElement.appendChild(errorDiv);
    }

    showSuccess(fieldName) {
        const field = this.form.querySelector(`[name="${fieldName}"], #${fieldName}`);
        if (!field) return;

        field.classList.add('border-green-500');
        field.classList.remove('border-red-500');

        // Remove error message if exists
        const existingError = field.parentElement.querySelector('.error-message');
        if (existingError) existingError.remove();
    }

    clearErrors() {
        const errorMessages = this.form.querySelectorAll('.error-message');
        errorMessages.forEach(msg => msg.remove());

        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.classList.remove('border-red-500', 'border-green-500');
        });
    }

    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    validateEnrollment(enrollment) {
        // Accept 10-12 digit numbers or email format
        return /^\d{10,12}$/.test(enrollment) || this.validateEmail(enrollment);
    }

    validatePhone(phone) {
        const cleaned = phone.replace(/\D/g, '');
        return /^[6-9]\d{9}$/.test(cleaned);
    }

    validatePassword(password) {
        return password.length >= 8;
    }
};

// Add CSS animations
if (!document.getElementById('gec-utils-styles')) {
    const style = document.createElement('style');
    style.id = 'gec-utils-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}
