document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const gatewayOptions = document.querySelectorAll('.gateway-option');
    const paymentForms = document.querySelectorAll('.payment-form');
    const confirmBtn = document.getElementById('confirm-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const modal = document.getElementById('confirmation-modal');
    const modalDetails = document.getElementById('modal-details');
    const confirmWithdrawal = document.getElementById('confirm-withdrawal');
    const cancelWithdrawal = document.getElementById('cancel-withdrawal');

    // Current gateway state
    let currentGateway = null;
    
    // Load saved data from localStorage
    loadSavedData();
    
    // Gateway selection
    gatewayOptions.forEach(option => {
        option.addEventListener('click', function() {
            const gateway = this.getAttribute('data-gateway');
            
            // Add a small bounce effect when clicked
            this.classList.add('clicked');
            setTimeout(() => {
                this.classList.remove('clicked');
                selectGateway(gateway);
            }, 150);
        });
    });
    
    // Select gateway function
    function selectGateway(gateway) {
        // Remove active class from all options
        gatewayOptions.forEach(option => {
            option.classList.remove('active');
        });
        
        // Add active class to selected option
        document.querySelector(`.gateway-option[data-gateway="${gateway}"]`).classList.add('active');
        
        // Hide all forms
        paymentForms.forEach(form => {
            form.style.display = 'none';
        });
        
        // Show selected form
        document.getElementById(`${gateway}-form`).style.display = 'block';
        
        // Update current gateway
        currentGateway = gateway;
    }
    
    // Input event listeners for real-time validation and saving
    const allInputs = document.querySelectorAll('input');
    allInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateInput(this);
            saveDataToLocalStorage();
        });
    });
    
    // Validate input
    function validateInput(input) {
        const id = input.id;
        const value = input.value.trim();
        const errorElement = document.getElementById(`${id}-error`);
        
        // Clear previous error
        errorElement.textContent = '';
        
        // Phone number validation
        if (id.includes('phone')) {
            if (value === '') {
                errorElement.textContent = 'Phone number is required';
                return false;
            }
            if (!/^\d{10}$/.test(value)) {
                errorElement.textContent = 'Please enter a valid 10-digit phone number';
                return false;
            }
        }
        
        // Name validation
        if (id.includes('name')) {
            if (value === '') {
                errorElement.textContent = 'Name is required';
                return false;
            }
            if (value.length < 3) {
                errorElement.textContent = 'Name must be at least 3 characters';
                return false;
            }
        }
        
        // Binance ID validation
        if (id === 'binance-id') {
            if (value === '') {
                errorElement.textContent = 'Binance ID is required';
                return false;
            }
            if (value.length < 5) {
                errorElement.textContent = 'Please enter a valid Binance ID';
                return false;
            }
        }
        
        // Amount validation
        if (id.includes('amount')) {
            if (value === '') {
                errorElement.textContent = 'Amount is required';
                return false;
            }
            if (isNaN(value) || parseFloat(value) <= 0) {
                errorElement.textContent = 'Please enter a valid amount';
                return false;
            }
        }
        
        return true;
    }
    
    // Validate all inputs in current form
    function validateCurrentForm() {
        if (!currentGateway) return false;
        
        const inputs = document.querySelectorAll(`#${currentGateway}-form input`);
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Confirm button click
    confirmBtn.addEventListener('click', function(e) {
        if (!currentGateway) {
            alert('Please select a payment gateway');
            return;
        }
        
        // Add ripple effect on button click
        createRipple(e, this);
        
        if (validateCurrentForm()) {
            showConfirmationModal();
        } else {
            alert('Please fill in all required fields correctly');
        }
    });
    
    // Cancel button click
    cancelBtn.addEventListener('click', function(e) {
        // Add ripple effect on button click
        createRipple(e, this);
        resetForm();
    });
    
    // Show confirmation modal
    function showConfirmationModal() {
        let details = '';
        
        if (currentGateway === 'mtn') {
            details = `
                <p><strong>Gateway:</strong> MTN Ghana</p>
                <p><strong>Name:</strong> ${document.getElementById('mtn-name').value}</p>
                <p><strong>Phone Number:</strong> ${document.getElementById('mtn-phone').value}</p>
                <p><strong>Amount:</strong> GHC ${document.getElementById('mtn-amount').value}</p>
            `;
        } else if (currentGateway === 'vodafone') {
            details = `
                <p><strong>Gateway:</strong> Vodafone Ghana</p>
                <p><strong>Name:</strong> ${document.getElementById('vodafone-name').value}</p>
                <p><strong>Phone Number:</strong> ${document.getElementById('vodafone-phone').value}</p>
                <p><strong>Amount:</strong> GHC ${document.getElementById('vodafone-amount').value}</p>
            `;
        } else if (currentGateway === 'binance') {
            details = `
                <p><strong>Gateway:</strong> Binance</p>
                <p><strong>Binance ID:</strong> ${document.getElementById('binance-id').value}</p>
                <p><strong>Amount:</strong> USD ${document.getElementById('binance-amount').value}</p>
            `;
        }
        
        modalDetails.innerHTML = details;
        modal.style.display = 'flex';
    }
    
    // Confirm withdrawal button in modal
    confirmWithdrawal.addEventListener('click', function(e) {
        // Add ripple effect on button click
        createRipple(e, this);
        
        // Here you would normally send the data to a server
        alert('Withdrawal request submitted successfully!');
        modal.style.display = 'none';
        
        // Clear form after successful submission
        resetForm();
    });
    
    // Cancel withdrawal button in modal
    cancelWithdrawal.addEventListener('click', function(e) {
        // Add ripple effect on button click
        createRipple(e, this);
        modal.style.display = 'none';
    });
    
    // Reset form
    function resetForm() {
        // Clear all inputs
        allInputs.forEach(input => {
            input.value = '';
        });
        
        // Clear all error messages
        document.querySelectorAll('.error-message').forEach(error => {
            error.textContent = '';
        });
        
        // Reset gateway selection
        gatewayOptions.forEach(option => {
            option.classList.remove('active');
        });
        
        // Hide all forms
        paymentForms.forEach(form => {
            form.style.display = 'none';
        });
        
        // Reset current gateway
        currentGateway = null;
        
        // Clear localStorage
        localStorage.removeItem('paymentData');
    }
    
    // Save data to localStorage
    function saveDataToLocalStorage() {
        const data = {
            mtn: {
                name: document.getElementById('mtn-name').value,
                phone: document.getElementById('mtn-phone').value,
                amount: document.getElementById('mtn-amount').value
            },
            vodafone: {
                name: document.getElementById('vodafone-name').value,
                phone: document.getElementById('vodafone-phone').value,
                amount: document.getElementById('vodafone-amount').value
            },
            binance: {
                id: document.getElementById('binance-id').value,
                amount: document.getElementById('binance-amount').value
            },
            lastGateway: currentGateway
        };
        
        localStorage.setItem('paymentData', JSON.stringify(data));
    }
    
    // Load data from localStorage
    function loadSavedData() {
        const savedData = localStorage.getItem('paymentData');
        if (savedData) {
            const data = JSON.parse(savedData);
            
            // Populate MTN fields
            document.getElementById('mtn-name').value = data.mtn.name || '';
            document.getElementById('mtn-phone').value = data.mtn.phone || '';
            document.getElementById('mtn-amount').value = data.mtn.amount || '';
            
            // Populate Vodafone fields
            document.getElementById('vodafone-name').value = data.vodafone.name || '';
            document.getElementById('vodafone-phone').value = data.vodafone.phone || '';
            document.getElementById('vodafone-amount').value = data.vodafone.amount || '';
            
            // Populate Binance fields
            document.getElementById('binance-id').value = data.binance.id || '';
            document.getElementById('binance-amount').value = data.binance.amount || '';
            
            // Set last used gateway if any
            if (data.lastGateway) {
                selectGateway(data.lastGateway);
            }
        }
    }
    
    // Create ripple effect for buttons
    function createRipple(event, button) {
        const circle = document.createElement('span');
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;
        
        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
        circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
        circle.classList.add('button-ripple');
        
        // Remove existing ripples
        const ripple = button.getElementsByClassName('button-ripple')[0];
        if (ripple) {
            ripple.remove();
        }
        
        button.appendChild(circle);
        
        // Add pulse effect temporarily
        button.classList.add('pulse-effect');
        setTimeout(() => {
            button.classList.remove('pulse-effect');
        }, 600);
        
        // Move button slightly when clicked
        button.style.transform = 'translateY(2px)';
        setTimeout(() => {
            button.style.transform = '';
        }, 200);
    }
    
    // Remove ripple after animation completes
    document.addEventListener('animationend', function(e) {
        if (e.animationName === 'ripple') {
            e.target.remove();
        }
    });
    
    // Close modal if user clicks outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Add event listener for screen resize
    window.addEventListener('resize', adjustLayoutForScreenSize);
    
    // Call once on load to set initial layout
    adjustLayoutForScreenSize();
    
    function adjustLayoutForScreenSize() {
        const screenWidth = window.innerWidth;
        
        // Adjust text size based on screen width
        if (screenWidth < 480) {
            document.querySelectorAll('.gateway-option p').forEach(p => {
                p.style.fontSize = '14px';
            });
        } else {
            document.querySelectorAll('.gateway-option p').forEach(p => {
                p.style.fontSize = '16px';
            });
        }
    }
});