// static/js/core.js - File chính quản lý toàn bộ chức năng
document.addEventListener("DOMContentLoaded", function() {
    console.log("App initialized");
    
    // Khởi tạo các module
    AuthModule.init();
    DarkModeModule.init();
    NavigationModule.init();
    PostModule.init();
    CommentModule.init();
});

// Module quản lý xác thực
const AuthModule = {
    init: function() {
        this.setupPasswordToggle();
        this.setupFormValidation();
    },
    
    setupPasswordToggle: function() {
        const togglePassword = document.getElementById('togglePassword');
        if (!togglePassword) return;

        togglePassword.addEventListener('change', function() {
            const passwordFields = document.querySelectorAll('.password-field');
            const type = this.checked ? 'text' : 'password';
            passwordFields.forEach(field => field.type = type);
        });
    },
    
    setupFormValidation: function() {
        // ... (giữ nguyên logic validation từ auth.js)
    }
};

// Module chế độ tối
const DarkModeModule = {
    init: function() {
        const toggleBtn = document.getElementById('darkModeToggle');
        if (!toggleBtn) return;

        // Khôi phục trạng thái từ localStorage
        const isDark = localStorage.getItem('darkMode') === 'enabled';
        this.setDarkMode(isDark);

        toggleBtn.addEventListener('click', () => {
            const isDark = document.body.classList.contains('dark-mode');
            this.setDarkMode(!isDark);
        });
    },
    
    setDarkMode: function(enabled) {
        document.body.classList.toggle('dark-mode', enabled);
        localStorage.setItem('darkMode', enabled ? 'enabled' : 'disabled');
        
        const icon = document.getElementById('darkModeIcon');
        if (icon) {
            icon.className = enabled ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
};

// Module điều hướng
const NavigationModule = {
    init: function() {
        this.setupMobileMenu();
    },
    
    setupMobileMenu: function() {
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('open');
            });
        }
    }
};