// static/js/helpers.js
class Toast {
    static show(message, type = 'success', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s forwards';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }
}

class FormHelper {
    static serialize(form) {
        const data = new FormData(form);
        return new URLSearchParams(data);
    }
    
    static clearErrors(form) {
        form.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });
    }
    
    static showErrors(form, errors) {
        this.clearErrors(form);
        
        Object.entries(errors).forEach(([field, messages]) => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback';
                errorDiv.textContent = messages.join(', ');
                input.parentNode.appendChild(errorDiv);
            }
        });
    }
}