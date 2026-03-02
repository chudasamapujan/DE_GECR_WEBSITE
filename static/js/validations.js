// Form validation utilities - Additional validators
// Note: Main GECUtils including FormValidator is in api.js

// This file can be used for additional validation helpers
window.GECUtils = window.GECUtils || {};

// Additional validation utilities
GECUtils.Validators = {
    isNumeric: function(value) {
        return /^\d+$/.test(value);
    },
    
    isAlpha: function(value) {
        return /^[a-zA-Z\s]+$/.test(value);
    },
    
    isAlphanumeric: function(value) {
        return /^[a-zA-Z0-9\s]+$/.test(value);
    },
    
    minLength: function(value, min) {
        return value.length >= min;
    },
    
    maxLength: function(value, max) {
        return value.length <= max;
    },
    
    inRange: function(value, min, max) {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && num <= max;
    }
};
