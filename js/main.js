// Global JavaScript functionality for GEC Rajkot Website

// Form validation utilities
class FormValidator {
    constructor(form) {
        this.form = form;
        this.errors = {};
    }

    // Email validation
    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    // Phone validation
    validatePhone(phone) {
        const phoneRegex = /^[6-9]\d{9}$/;
        return phoneRegex.test(phone);
    }

    // Enrollment number validation
    validateEnrollment(enrollment) {
        const enrollmentRegex = /^[0-9]{10,12}$/;
        return enrollmentRegex.test(enrollment);
    }

    // Faculty ID validation
    validateFacultyId(facultyId) {
        const facultyIdRegex = /^[A-Z]{2,3}[0-9]{3,5}$/;
        return facultyIdRegex.test(facultyId);
    }

    // Password strength validation
    validatePassword(password) {
        const minLength = 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(password);

        return {
            isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers && hasSpecial,
            length: password.length >= minLength,
            uppercase: hasUpperCase,
            lowercase: hasLowerCase,
            numbers: hasNumbers,
            special: hasSpecial
        };
    }

    // Show error message
    showError(fieldName, message) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('error');
            field.classList.remove('success');
            
            // Remove existing error message
            const existingError = field.parentNode.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            
            // Add new error message
            const errorElement = document.createElement('span');
            errorElement.className = 'error-message';
            errorElement.textContent = message;
            field.parentNode.appendChild(errorElement);
        }
    }

    // Show success state
    showSuccess(fieldName) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('success');
            field.classList.remove('error');
            
            // Remove error message
            const errorMessage = field.parentNode.querySelector('.error-message');
            if (errorMessage) {
                errorMessage.remove();
            }
        }
    }

    // Clear all errors
    clearErrors() {
        const errorInputs = this.form.querySelectorAll('.error');
        const errorMessages = this.form.querySelectorAll('.error-message');
        
        errorInputs.forEach(input => {
            input.classList.remove('error', 'success');
        });
        
        errorMessages.forEach(message => {
            message.remove();
        });
    }
}

// Animation utilities
class AnimationUtils {
    static fadeIn(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const opacity = Math.min(progress / duration, 1);
            
            element.style.opacity = opacity;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }

    static slideIn(element, direction = 'left', duration = 300) {
        const translateX = direction === 'left' ? '-100%' : '100%';
        
        element.style.transform = `translateX(${translateX})`;
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        const animate = (timestamp) => {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const percentage = Math.min(progress / duration, 1);
            
            element.style.transform = `translateX(${parseInt(translateX) * (1 - percentage)}%)`;
            element.style.opacity = percentage;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            } else {
                element.style.transform = 'translateX(0)';
                element.style.opacity = '1';
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// Toast notification system
class ToastManager {
    constructor() {
        this.createContainer();
    }

    createContainer() {
        if (!document.getElementById('toast-container')) {
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
            `;
            document.body.appendChild(container);
        }
    }

    show(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} animate-slide-in`;
        toast.style.cssText = `
            min-width: 300px;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            cursor: pointer;
        `;
        toast.textContent = message;

        // Add close functionality
        toast.addEventListener('click', () => {
            this.remove(toast);
        });

        // Auto remove after duration
        setTimeout(() => {
            this.remove(toast);
        }, duration);

        document.getElementById('toast-container').appendChild(toast);
    }

    remove(toast) {
        toast.style.transform = 'translateX(100%)';
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        this.show(message, 'error', duration);
    }

    warning(message, duration = 4000) {
        this.show(message, 'warning', duration);
    }

    info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
}

// Modal system
class ModalManager {
    constructor() {
        this.activeModal = null;
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.activeModal) {
                this.close();
            }
        });
    }

    create(options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content glass-card';
        modalContent.style.cssText = `
            max-width: ${options.maxWidth || '500px'};
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
            transform: scale(0.95);
            transition: transform 0.3s ease;
        `;

        if (options.title) {
            const header = document.createElement('div');
            header.className = 'card-header flex-between';
            header.innerHTML = `
                <h3 class="card-title">${options.title}</h3>
                <button class="modal-close btn btn-secondary btn-sm">×</button>
            `;
            modalContent.appendChild(header);
        }

        if (options.content) {
            const body = document.createElement('div');
            body.className = 'modal-body';
            body.innerHTML = options.content;
            modalContent.appendChild(body);
        }

        modal.appendChild(modalContent);
        document.body.appendChild(modal);

        // Animation
        setTimeout(() => {
            modal.style.opacity = '1';
            modalContent.style.transform = 'scale(1)';
        }, 10);

        // Close functionality
        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('modal-close')) {
                this.close();
            }
        });

        this.activeModal = modal;
        return modal;
    }

    close() {
        if (this.activeModal) {
            const modal = this.activeModal;
            const content = modal.querySelector('.modal-content');
            
            modal.style.opacity = '0';
            content.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
            
            this.activeModal = null;
        }
    }
}

// Loading states
class LoadingManager {
    static setLoading(element, isLoading = true) {
        if (isLoading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }

    static showGlobalLoader() {
        let loader = document.getElementById('global-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            `;
            loader.innerHTML = `
                <div style="text-align: center;">
                    <div class="animate-spin" style="width: 40px; height: 40px; border: 4px solid #e5e7eb; border-top: 4px solid #4f46e5; border-radius: 50%; margin: 0 auto 16px;"></div>
                    <p style="color: #6b7280;">Loading...</p>
                </div>
            `;
            document.body.appendChild(loader);
        }
        loader.style.display = 'flex';
    }

    static hideGlobalLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }
}

// Initialize global instances
const toast = new ToastManager();
const modal = new ModalManager();

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Form submission handler
function setupFormSubmission() {
    document.addEventListener('submit', async (e) => {
        const form = e.target;
        if (form.tagName === 'FORM' && form.dataset.ajax === 'true') {
            e.preventDefault();
            
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            LoadingManager.setLoading(submitBtn, true);
            
            try {
                const formData = new FormData(form);
                const response = await fetch(form.action || '#', {
                    method: form.method || 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    toast.success(result.message || 'Operation completed successfully!');
                    if (result.redirect) {
                        setTimeout(() => {
                            window.location.href = result.redirect;
                        }, 1000);
                    }
                } else {
                    toast.error(result.message || 'An error occurred. Please try again.');
                }
            } catch (error) {
                console.error('Form submission error:', error);
                toast.error('Network error. Please check your connection and try again.');
            } finally {
                LoadingManager.setLoading(submitBtn, false);
                submitBtn.textContent = originalText;
            }
        }
    });
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    setupFormSubmission();
    
    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation to elements when they come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.card, .glass-card').forEach(el => {
        observer.observe(el);
    });
});

// Export for use in other scripts
window.GECUtils = {
    FormValidator,
    AnimationUtils,
    ToastManager,
    ModalManager,
    LoadingManager,
    toast,
    modal,
    debounce,
    throttle
};