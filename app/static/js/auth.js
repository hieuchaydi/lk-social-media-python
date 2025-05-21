// static/js/auth.js
document.addEventListener('DOMContentLoaded', function() {
    // ========== TOGGLE PASSWORD VISIBILITY ==========
    const togglePassword = document.getElementById('togglePassword');
    if (togglePassword) {
        togglePassword.addEventListener('change', function() {
            const passwordFields = document.querySelectorAll('.password-field');
            const type = this.checked ? 'text' : 'password';
            const eyeIcon = document.getElementById('eyeIcon');
            
            passwordFields.forEach(field => {
                field.type = type;
            });

            // Đổi icon eye
            if (eyeIcon) {
                eyeIcon.className = this.checked ? 'fas fa-eye-slash' : 'fas fa-eye';
            }
        });
    }

    // ========== REAL-TIME VALIDATION ==========
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');
        
        inputs.forEach(input => {
            // Validate khi blur khỏi input
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            // Remove error khi bắt đầu nhập
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const errorElement = this.nextElementSibling;
                    if (errorElement && errorElement.classList.contains('invalid-feedback')) {
                        errorElement.remove();
                    }
                }
            });
        });
    });

    // ========== PASSWORD STRENGTH METER ==========
    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }

    // ========== CONFIRM PASSWORD MATCHING ==========
    const confirmPassword = document.getElementById('confirm');
    if (confirmPassword) {
        confirmPassword.addEventListener('input', function() {
            const password = document.getElementById('password').value;
            validatePasswordMatch(password, this.value);
        });
    }

    // ========== FORM SUBMIT VALIDATION ==========
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            const inputs = this.querySelectorAll('input[required]');
            
            inputs.forEach(input => {
                if (!validateInput(input)) {
                    isValid = false;
                }
            });

            // Kiểm tra match password nếu là form đăng ký
            if (this.querySelector('#confirm')) {
                const password = document.getElementById('password').value;
                const confirm = document.getElementById('confirm').value;
                
                if (!validatePasswordMatch(password, confirm)) {
                    isValid = false;
                }
            }

            if (!isValid) {
                e.preventDefault();
                // Cuộn đến lỗi đầu tiên
                const firstError = this.querySelector('.is-invalid');
                if (firstError) {
                    firstError.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }
            }
        });
    });
});

// ========== HELPER FUNCTIONS ==========
function validateInput(input) {
    let isValid = true;
    const value = input.value.trim();
    const errorElement = input.nextElementSibling;
    
    // Kiểm tra required
    if (!value) {
        showError(input, 'Vui lòng điền vào trường này');
        isValid = false;
    }
    // Kiểm tra email format
    else if (input.type === 'email' && !validateEmail(value)) {
        showError(input, 'Email không hợp lệ');
        isValid = false;
    }
    // Kiểm tra username (chỉ cho phép chữ, số và _)
    else if (input.name === 'username' && !/^[a-zA-Z0-9_]+$/.test(value)) {
        showError(input, 'Tên người dùng chỉ được chứa chữ cái, số và dấu gạch dưới');
        isValid = false;
    }
    
    return isValid;
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(input, message) {
    input.classList.add('is-invalid');
    
    // Kiểm tra nếu đã có thông báo lỗi thì không thêm nữa
    let errorElement = input.nextElementSibling;
    if (!errorElement || !errorElement.classList.contains('invalid-feedback')) {
        errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        input.parentNode.insertBefore(errorElement, input.nextSibling);
    }
    
    errorElement.textContent = message;
}

function checkPasswordStrength(password) {
    const strengthMeter = document.getElementById('password-strength');
    if (!strengthMeter) return;

    let strength = 0;
    let messages = [];

    // Kiểm tra độ dài
    if (password.length < 8) {
        messages.push('Quá ngắn (tối thiểu 8 ký tự)');
    } else {
        strength += 1;
    }

    // Kiểm tra chữ hoa
    if (!/[A-Z]/.test(password)) {
        messages.push('Nên có ít nhất 1 chữ hoa');
    } else {
        strength += 1;
    }

    // Kiểm tra số
    if (!/[0-9]/.test(password)) {
        messages.push('Nên có ít nhất 1 số');
    } else {
        strength += 1;
    }

    // Kiểm tra ký tự đặc biệt
    if (!/[^A-Za-z0-9]/.test(password)) {
        messages.push('Nên có ít nhất 1 ký tự đặc biệt');
    } else {
        strength += 1;
    }

    // Cập nhật giao diện
    const strengthText = ['Rất yếu', 'Yếu', 'Trung bình', 'Mạnh', 'Rất mạnh'];
    const strengthClass = ['very-weak', 'weak', 'medium', 'strong', 'very-strong'];
    
    strengthMeter.textContent = strengthText[strength];
    strengthMeter.className = 'password-strength ' + strengthClass[strength];

    // Hiển thị gợi ý
    const suggestions = document.getElementById('password-suggestions');
    if (suggestions) {
        if (messages.length > 0 && password.length > 0) {
            suggestions.innerHTML = '<strong>Gợi ý:</strong> ' + messages.join(', ');
        } else {
            suggestions.innerHTML = '';
        }
    }
}

function validatePasswordMatch(password, confirmPassword) {
    const confirmField = document.getElementById('confirm');
    if (!confirmField) return true;

    if (password !== confirmPassword) {
        showError(confirmField, 'Mật khẩu không khớp');
        return false;
    } else {
        confirmField.classList.remove('is-invalid');
        const errorElement = confirmField.nextElementSibling;
        if (errorElement && errorElement.classList.contains('invalid-feedback')) {
            errorElement.remove();
        }
        return true;
    }
}