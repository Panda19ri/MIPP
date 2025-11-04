// Medical Insurance Premium Prediction - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize animations
    initializeAnimations();
    
    // Initialize charts if present
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Auto-hide alerts after 5 seconds
    autoHideAlerts();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Form validation enhancements
function initializeFormValidations() {
    // Age validation
    const ageInputs = document.querySelectorAll('input[name="age"]');
    ageInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateAge(this);
        });
    });
    
    // BMI validation
    const bmiInputs = document.querySelectorAll('input[name="bmi"]');
    bmiInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateBMI(this);
        });
    });
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateEmail(this);
        });
    });
}

// Age validation function
function validateAge(input) {
    const age = parseInt(input.value);
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (age < 18 || age > 100) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        feedback.textContent = 'Age must be between 18 and 100 years.';
    } else if (age >= 18 && age <= 100) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        feedback.textContent = '';
    }
}

// BMI validation function
function validateBMI(input) {
    const bmi = parseFloat(input.value);
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (bmi < 10 || bmi > 50) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        feedback.textContent = 'BMI must be between 10 and 50.';
    } else if (bmi >= 10 && bmi <= 50) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        feedback.textContent = getBMICategory(bmi);
        
        // Add BMI category color
        if (bmi < 18.5) {
            input.style.borderColor = '#17a2b8';
        } else if (bmi < 25) {
            input.style.borderColor = '#28a745';
        } else if (bmi < 30) {
            input.style.borderColor = '#ffc107';
        } else {
            input.style.borderColor = '#dc3545';
        }
    }
}

// Email validation function
function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const feedback = input.parentNode.querySelector('.invalid-feedback') || createFeedbackElement(input);
    
    if (!emailRegex.test(email)) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        feedback.textContent = 'Please enter a valid email address.';
    } else {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
        feedback.textContent = '';
    }
}

// Create feedback element
function createFeedbackElement(input) {
    const feedback = document.createElement('div');
    feedback.className = 'invalid-feedback';
    input.parentNode.appendChild(feedback);
    return feedback;
}

// Get BMI category
function getBMICategory(bmi) {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
}

// BMI Calculator function
function calculateBMI() {
    const height = document.getElementById('height')?.value;
    const weight = document.getElementById('weight')?.value;
    
    if (height && weight) {
        const heightM = height / 100;
        const bmi = (weight / (heightM * heightM)).toFixed(1);
        
        const category = getBMICategory(parseFloat(bmi));
        let colorClass = '';
        
        if (bmi < 18.5) colorClass = 'text-info';
        else if (bmi < 25) colorClass = 'text-success';
        else if (bmi < 30) colorClass = 'text-warning';
        else colorClass = 'text-danger';
        
        const resultDiv = document.getElementById('bmiResult');
        if (resultDiv) {
            resultDiv.innerHTML = 
                `<strong>Your BMI: <span class="${colorClass}">${bmi}</span> (${category})</strong>`;
            
            // Auto-fill BMI in the main form
            const bmiInput = document.getElementById('bmi');
            if (bmiInput) {
                bmiInput.value = bmi;
                validateBMI(bmiInput);
            }
        }
    } else {
        const resultDiv = document.getElementById('bmiResult');
        if (resultDiv) {
            resultDiv.innerHTML = '<span class="text-danger">Please enter both height and weight</span>';
        }
    }
}

// Password visibility toggle
function togglePasswordVisibility(buttonId, inputId) {
    const button = document.getElementById(buttonId);
    const input = document.getElementById(inputId);
    
    if (button && input) {
        button.addEventListener('click', function() {
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    }
}

// Initialize animations
function initializeAnimations() {
    // Fade in elements
    const elements = document.querySelectorAll('.card, .alert');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Auto-hide alerts
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// AJAX form submission for predictions
function submitPredictionAJAX(formData) {
    return fetch('/user/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(`Predicted Premium: ${data.formatted_prediction}`);
        } else {
            showErrorMessage(data.error || 'Prediction failed');
        }
        return data;
    })
    .catch(error => {
        showErrorMessage('Network error occurred');
        console.error('Error:', error);
    });
}

// Show success message
function showSuccessMessage(message) {
    showMessage(message, 'success');
}

// Show error message
function showErrorMessage(message) {
    showMessage(message, 'danger');
}

// Show message function
function showMessage(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }, 5000);
    }
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Loading overlay functions
function showLoadingOverlay(text = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
    overlay.style.zIndex = '9999';
    
    overlay.innerHTML = `
        <div class="bg-white p-4 rounded text-center">
            <div class="spinner-border text-primary mb-3" role="status"></div>
            <p class="mb-0">${text}</p>
        </div>
    `;
    
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.remove();
    }
}

// Table sorting functionality
function sortTable(table, column, direction = 'asc') {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const sortedRows = rows.sort((a, b) => {
        const aValue = a.querySelectorAll('td')[column].textContent.trim();
        const bValue = b.querySelectorAll('td')[column].textContent.trim();
        
        if (direction === 'asc') {
            return aValue.localeCompare(bValue, undefined, {numeric: true});
        } else {
            return bValue.localeCompare(aValue, undefined, {numeric: true});
        }
    });
    
    // Remove existing rows
    tbody.innerHTML = '';
    
    // Add sorted rows
    sortedRows.forEach(row => tbody.appendChild(row));
}

// Initialize charts (if Chart.js is available)
function initializeCharts() {
    // This will be implemented when we add chart functionality
    console.log('Chart initialization ready');
}

// Data export functionality
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = Array.from(cols).map(col => {
            let data = col.textContent.trim();
            // Escape quotes and wrap in quotes if contains comma
            if (data.includes(',') || data.includes('"')) {
                data = '"' + data.replace(/"/g, '""') + '"';
            }
            return data;
        });
        csv.push(rowData.join(','));
    });
    
    // Download CSV
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

// Real-time form validation
function enableRealTimeValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
}

// Validate individual field
function validateField(field) {
    const value = field.value.trim();
    const type = field.type;
    const name = field.name;
    
    // Remove existing validation classes
    field.classList.remove('is-valid', 'is-invalid');
    
    // Check if required and empty
    if (field.hasAttribute('required') && !value) {
        field.classList.add('is-invalid');
        return false;
    }
    
    // Type-specific validations
    switch (name) {
        case 'age':
            return validateAge(field);
        case 'bmi':
            return validateBMI(field);
        case 'email':
            return validateEmail(field);
        default:
            if (value) {
                field.classList.add('is-valid');
            }
            return true;
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccessMessage('Copied to clipboard!');
    }).catch(err => {
        showErrorMessage('Failed to copy to clipboard');
    });
}

// Mobile menu handling
function handleMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            }
        });
        
        // Close menu when clicking on nav links
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                const bsCollapse = bootstrap.Collapse.getInstance(navbarCollapse);
                if (bsCollapse) {
                    bsCollapse.hide();
                }
            });
        });
    }
}

// Initialize mobile menu handling
handleMobileMenu();

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // In production, you might want to send this to a logging service
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load time
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log('Page load time:', loadTime + 'ms');
});

// Service worker registration (for future PWA functionality)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // navigator.serviceWorker.register('/sw.js'); // Uncomment when PWA is implemented
    });
}