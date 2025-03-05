document.addEventListener('DOMContentLoaded', () => {
    // Get elements
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const toggleConfirmPasswordBtn = document.getElementById('toggleConfirmPassword');
    const strengthText = document.getElementById('strength-text');
    const matchStatus = document.getElementById('matchStatus');
    const submitBtn = document.getElementById('submitBtn');
    
    // Password requirement elements
    const lengthReq = document.getElementById('length');
    const uppercaseReq = document.getElementById('uppercase');
    const lowercaseReq = document.getElementById('lowercase');
    const numberReq = document.getElementById('number');
    const specialReq = document.getElementById('special');
    
    // Toggle password visibility
    function togglePasswordVisibility(inputElement, toggleButton) {
        toggleButton.classList.toggle('showing-password');
        inputElement.type = inputElement.type === 'password' ? 'text' : 'password';
    }
    
    togglePasswordBtn.addEventListener('click', () => {
        togglePasswordVisibility(passwordInput, togglePasswordBtn);
    });
    
    toggleConfirmPasswordBtn.addEventListener('click', () => {
        togglePasswordVisibility(confirmPasswordInput, toggleConfirmPasswordBtn);
    });
    
    // Check password strength
    function checkPasswordStrength(password) {
        let score = 0;
        const strengthMeter = document.querySelector('.password-strength');
        
        // Reset classes
        strengthMeter.classList.remove('strength-weak', 'strength-medium', 'strength-good', 'strength-strong');
        
        if (!password) {
            strengthText.textContent = 'Password strength';
            return;
        }
        
        // Check length
        if (password.length >= 8) {
            score++;
            lengthReq.classList.add('valid');
        } else {
            lengthReq.classList.remove('valid');
        }
        
        // Check for uppercase letters
        if (/[A-Z]/.test(password)) {
            score++;
            uppercaseReq.classList.add('valid');
        } else {
            uppercaseReq.classList.remove('valid');
        }
        
        // Check for lowercase letters
        if (/[a-z]/.test(password)) {
            score++;
            lowercaseReq.classList.add('valid');
        } else {
            lowercaseReq.classList.remove('valid');
        }
        
        // Check for numbers
        if (/\d/.test(password)) {
            score++;
            numberReq.classList.add('valid');
        } else {
            numberReq.classList.remove('valid');
        }
        
        // Check for special characters
        if (/[^A-Za-z0-9]/.test(password)) {
            score++;
            specialReq.classList.add('valid');
        } else {
            specialReq.classList.remove('valid');
        }
        
        // Update strength indicator based on score
        if (password.length === 0) {
            strengthText.textContent = 'Password strength';
        } else if (score <= 2) {
            strengthMeter.classList.add('strength-weak');
            strengthText.textContent = 'Weak';
        } else if (score === 3) {
            strengthMeter.classList.add('strength-medium');
            strengthText.textContent = 'Medium';
        } else if (score === 4) {
            strengthMeter.classList.add('strength-good');
            strengthText.textContent = 'Good';
        } else {
            strengthMeter.classList.add('strength-strong');
            strengthText.textContent = 'Strong';
        }
        
        checkFormValidity();
    }
    
    // Check if passwords match
    function checkPasswordMatch() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        if (!confirmPassword) {
            matchStatus.textContent = '';
            return;
        }
        
        if (password === confirmPassword) {
            matchStatus.textContent = 'Passwords match';
            matchStatus.style.color = '#27ae60';
        } else {
            matchStatus.textContent = 'Passwords do not match';
            matchStatus.style.color = '#e74c3c';
        }
        
        checkFormValidity();
    }
    
    // Check if form is valid to enable submit button
    function checkFormValidity() {
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const meetsRequirements = 
            password.length >= 8 &&
            /[A-Z]/.test(password) &&
            /[a-z]/.test(password) &&
            /\d/.test(password) &&
            /[^A-Za-z0-9]/.test(password);
        
        submitBtn.disabled = !(meetsRequirements && password === confirmPassword && confirmPassword !== '');
    }
    
    // Event listeners
    passwordInput.addEventListener('input', () => {
        checkPasswordStrength(passwordInput.value);
        if (confirmPasswordInput.value) {
            checkPasswordMatch();
        }
    });
    
    confirmPasswordInput.addEventListener('input', checkPasswordMatch);
    
    // Submit form
    submitBtn.addEventListener('click', () => {
        alert('Password successfully set!');
        // In a real application, you would submit to server here
    });
});