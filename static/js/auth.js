// ===== AUTHENTICATION PAGE FUNCTIONALITY =====

class AuthPage {
    constructor() {
        this.form = document.getElementById('auth-login-form') || document.getElementById('auth-register-form');
        this.isRegisterPage = !!document.getElementById('auth-register-form');

        if (this.isRegisterPage) {
            this.initRegisterPage();
        } else {
            this.initLoginPage();
        }

        this.initCommonElements();
        this.init();
    }

    initLoginPage() {
        this.usernameInput = document.getElementById('auth-username');
        this.passwordInput = document.getElementById('auth-password');
        this.submitButton = document.getElementById('auth-submit-button');
        this.togglePasswordButton = document.getElementById('auth-toggle-password');
        this.eyeIcon = document.getElementById('auth-eye-icon');
        this.rememberCheckbox = document.getElementById('auth-remember');
    }

    initRegisterPage() {
        this.firstNameInput = document.getElementById('auth-first_name');
        this.lastNameInput = document.getElementById('auth-last_name');
        this.usernameInput = document.getElementById('auth-username');
        this.emailInput = document.getElementById('auth-email');
        this.passwordInput = document.getElementById('auth-password');
        this.confirmPasswordInput = document.getElementById('auth-confirm_password');
        this.submitButton = document.getElementById('auth-submit-button');
        this.termsCheckbox = document.getElementById('auth-terms');
        this.newsletterCheckbox = document.getElementById('auth-newsletter');
    }

    initCommonElements() {
        this.socialButtons = document.querySelectorAll('.auth-social-button');
        this.counters = document.querySelectorAll('[data-count]');
        this.togglePasswordButtons = document.querySelectorAll('.auth-password-toggle');
        this.allInputs = document.querySelectorAll('.auth-form-input');
        this.formGroups = document.querySelectorAll('.auth-form-group');
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupDemoData();

        if (this.isRegisterPage) {
            this.setupRegisterValidation();
            console.log('Register page initialized 📝');
        } else {
            this.setupLoginValidation();
            console.log('Login page initialized 🔐');
        }
    }

    setupEventListeners() {
        // Form submission
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Password toggle buttons
        this.togglePasswordButtons.forEach(button => {
            button.addEventListener('click', (e) => this.togglePasswordVisibility(e.currentTarget));
        });

        // Social buttons
        this.socialButtons.forEach(button => {
            button.addEventListener('click', (e) => this.handleSocialAuth(e));
        });

        // Input focus effects
        this.allInputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    input.parentElement.classList.remove('focused');
                }
                this.validateInput(input);
            });

            // Add validation on input
            input.addEventListener('input', () => {
                this.validateInput(input);
            });
        });

        // Remember me functionality (login only)
        if (!this.isRegisterPage && this.rememberCheckbox) {
            this.rememberCheckbox.addEventListener('change', () => {
                this.handleRememberMe();
            });
        }

        // Terms checkbox (register only)
        if (this.isRegisterPage && this.termsCheckbox) {
            this.termsCheckbox.addEventListener('change', () => {
                this.validateTerms();
            });
        }

        // Auto-fill demo data on double click
        if (this.usernameInput) {
            this.usernameInput.addEventListener('dblclick', () => {
                this.fillDemoData();
            });
        }

        // Handle Enter key submission
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && this.form && !e.target.matches('.auth-social-button')) {
                e.preventDefault();
                this.submitForm();
            }
        });
    }

    setupAnimations() {
        // Animate counters in banner
        if (this.counters.length > 0 && 'IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -100px 0px'
            });

            this.counters.forEach(counter => {
                observer.observe(counter);
            });
        }
    }

    setupLoginValidation() {
        // Initialize form validation for login
        if (this.usernameInput) {
            this.validateInput(this.usernameInput);
        }

        if (this.passwordInput) {
            this.validateInput(this.passwordInput);
        }
    }

    setupRegisterValidation() {
        // Initialize form validation for register
        if (this.firstNameInput) {
            this.validateInput(this.firstNameInput);
        }

        if (this.lastNameInput) {
            this.validateInput(this.lastNameInput);
        }

        if (this.usernameInput) {
            this.validateInput(this.usernameInput);
        }

        if (this.emailInput) {
            this.validateInput(this.emailInput);
        }

        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => {
                this.validatePassword();
            });
        }

        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => {
                this.validatePassword();
            });
        }
    }

    setupDemoData() {
        if (this.isRegisterPage) {
            // Demo data for register page
            const fields = {
                'auth-first_name': 'Иван',
                'auth-last_name': 'Иванов',
                'auth-username': 'ivanov',
                'auth-email': 'ivan@example.com',
                'auth-password': 'Demo123456',
                'auth-confirm_password': 'Demo123456'
            };

            Object.keys(fields).forEach(fieldId => {
                const field = document.getElementById(fieldId);
                if (field) {
                    field.addEventListener('dblclick', () => {
                        field.value = fields[fieldId];
                        this.validateInput(field);
                        if (fieldId.includes('password')) {
                            this.validatePassword();
                        }
                        this.showInfoMessage('Демо данные заполнены');
                    });
                }
            });
        } else {
            // Demo data for login page
            const savedUsername = localStorage.getItem('auth_username');
            const rememberChecked = localStorage.getItem('auth_remember') === 'true';

            if (savedUsername && this.usernameInput) {
                this.usernameInput.value = savedUsername;
            }

            if (rememberChecked && document.getElementById('auth-remember')) {
                document.getElementById('auth-remember').checked = true;
            }
        }
    }

    togglePasswordVisibility(button) {
        const inputGroup = button.closest('.auth-input-group');
        const input = inputGroup.querySelector('input[type="password"], input[type="text"]');
        const icon = button.querySelector('i');

        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);

        // Update eye icon
        if (type === 'text') {
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
            button.setAttribute('aria-label', 'Скрыть пароль');
        } else {
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
            button.setAttribute('aria-label', 'Показать пароль');
        }

        // Add animation
        icon.style.transform = 'scale(1.2)';
        setTimeout(() => {
            icon.style.transform = 'scale(1)';
        }, 200);
    }

    validateInput(input) {
        const value = input.value.trim();
        const parent = input.parentElement;

        // Remove previous validation states
        parent.classList.remove('valid', 'invalid');

        if (value === '') {
            return;
        }

        // Common validation for all inputs
        if (input.type === 'email' || input.getAttribute('name') === 'email') {
            // Email validation
            const isValid = this.isValidEmail(value);
            parent.classList.add(isValid ? 'valid' : 'invalid');
        } else if (input.type === 'text') {
            // Text validation
            if (input.getAttribute('name') === 'username') {
                const isValid = this.isValidUsername(value);
                parent.classList.add(isValid ? 'valid' : 'invalid');
            } else if (input.getAttribute('name') === 'first_name' || input.getAttribute('name') === 'last_name') {
                const isValid = value.length >= 2;
                parent.classList.add(isValid ? 'valid' : 'invalid');
            } else {
                // Generic text validation
                const isValid = value.length >= 3;
                parent.classList.add(isValid ? 'valid' : 'invalid');
            }
        } else if (input.type === 'password') {
            // Password validation
            const isValid = value.length >= 8;
            parent.classList.add(isValid ? 'valid' : 'invalid');
        }
    }

    validatePassword() {
        if (!this.isRegisterPage) return;

        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;

        // Clear previous states
        this.passwordInput.parentElement.classList.remove('valid', 'invalid');
        this.confirmPasswordInput.parentElement.classList.remove('valid', 'invalid');

        if (!password && !confirmPassword) return;

        // Check password strength
        const hasMinLength = password.length >= 8;
        const hasLetters = /[a-zA-Z]/.test(password);
        const hasNumbers = /\d/.test(password);

        if (password) {
            if (hasMinLength && hasLetters && hasNumbers) {
                this.passwordInput.parentElement.classList.add('valid');
            } else if (password.length > 0) {
                this.passwordInput.parentElement.classList.add('invalid');
            }
        }

        // Check password match
        if (password && confirmPassword) {
            if (password === confirmPassword && hasMinLength && hasLetters && hasNumbers) {
                this.confirmPasswordInput.parentElement.classList.add('valid');
            } else if (confirmPassword.length > 0) {
                this.confirmPasswordInput.parentElement.classList.add('invalid');
            }
        }
    }

    validateTerms() {
        if (!this.isRegisterPage) return;

        const termsChecked = this.termsCheckbox.checked;
        const label = this.termsCheckbox.closest('.auth-form-checkbox');

        if (label) {
            label.classList.remove('valid', 'invalid');
            if (!termsChecked && this.form.checkValidity()) {
                label.classList.add('invalid');
            }
        }
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidUsername(username) {
        const usernameRegex = /^[a-zA-Z0-9._]{3,}$/;
        return usernameRegex.test(username);
    }

    handleFormSubmit(e) {
        e.preventDefault();
        this.submitForm();
    }

    submitForm() {
        if (this.isRegisterPage) {
            this.submitRegisterForm();
        } else {
            this.submitLoginForm();
        }
    }

    submitLoginForm() {
        // Get form data
        const formData = new FormData(this.form);
        const username = formData.get('username') || '';
        const password = formData.get('password') || '';
        const remember = formData.get('remember') === 'on';

        // Validate form
        if (!this.validateLoginForm()) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        // Simulate API call
        this.simulateLogin(username, password, remember)
            .then(response => {
                this.showSuccessMessage('Вход выполнен успешно!');

                // Save credentials if "Remember me" is checked
                if (remember) {
                    localStorage.setItem('auth_username', username);
                    localStorage.setItem('auth_remember', 'true');
                } else {
                    localStorage.removeItem('auth_username');
                    localStorage.removeItem('auth_remember');
                }

                // Redirect after success (in a real app)
                setTimeout(() => {
                    // window.location.href = '/dashboard/';
                    console.log('Redirecting to dashboard...');
                }, 1500);
            })
            .catch(error => {
                this.showErrorMessage(error.message);
            })
            .finally(() => {
                this.setLoadingState(false);
            });
    }

    submitRegisterForm() {
        // Validate form
        if (!this.validateRegisterForm()) {
            return;
        }

        // Show loading state
        this.setLoadingState(true);

        // Simulate API call
        this.simulateRegister()
            .then(response => {
                this.showSuccessMessage('Регистрация прошла успешно! Проверьте вашу почту.');

                // Redirect to login page after 3 seconds
                setTimeout(() => {
                    window.location.href = '/accounts/login/';
                }, 3000);
            })
            .catch(error => {
                this.showErrorMessage(error.message);
            })
            .finally(() => {
                this.setLoadingState(false);
            });
    }

    validateLoginForm() {
        let isValid = true;
        const errors = [];

        // Validate username
        const username = this.usernameInput.value.trim();
        if (!username) {
            errors.push('Введите имя пользователя или email');
            isValid = false;
            this.usernameInput.parentElement.classList.add('invalid');
        } else if (!this.isValidEmail(username) && !this.isValidUsername(username)) {
            errors.push('Введите корректный email или имя пользователя');
            isValid = false;
            this.usernameInput.parentElement.classList.add('invalid');
        }

        // Validate password
        const password = this.passwordInput.value;
        if (!password) {
            errors.push('Введите пароль');
            isValid = false;
            this.passwordInput.parentElement.classList.add('invalid');
        } else if (password.length < 8) {
            errors.push('Пароль должен содержать минимум 8 символов');
            isValid = false;
            this.passwordInput.parentElement.classList.add('invalid');
        }

        // Show errors
        if (errors.length > 0) {
            this.showErrorMessage(errors.join('. '));
        }

        return isValid;
    }

    validateRegisterForm() {
        let isValid = true;
        const errors = [];

        // Validate all required fields
        const requiredFields = [
            { input: this.firstNameInput, name: 'Имя' },
            { input: this.lastNameInput, name: 'Фамилия' },
            { input: this.usernameInput, name: 'Имя пользователя' },
            { input: this.emailInput, name: 'Email' },
            { input: this.passwordInput, name: 'Пароль' },
            { input: this.confirmPasswordInput, name: 'Подтверждение пароля' }
        ];

        requiredFields.forEach(field => {
            if (field.input && !field.input.value.trim()) {
                errors.push(`Поле "${field.name}" обязательно для заполнения`);
                isValid = false;
                field.input.parentElement.classList.add('invalid');
            }
        });

        // Validate email
        if (this.emailInput && this.emailInput.value) {
            if (!this.isValidEmail(this.emailInput.value)) {
                errors.push('Введите корректный email адрес');
                isValid = false;
                this.emailInput.parentElement.classList.add('invalid');
            }
        }

        // Validate username
        if (this.usernameInput && this.usernameInput.value) {
            if (!this.isValidUsername(this.usernameInput.value)) {
                errors.push('Имя пользователя должно содержать только латинские буквы, цифры, точки и быть не менее 3 символов');
                isValid = false;
                this.usernameInput.parentElement.classList.add('invalid');
            }
        }

        // Validate password strength
        if (this.passwordInput && this.passwordInput.value) {
            const password = this.passwordInput.value;
            if (password.length < 8) {
                errors.push('Пароль должен содержать минимум 8 символов');
                isValid = false;
            }

            if (!/[a-zA-Z]/.test(password)) {
                errors.push('Пароль должен содержать буквы');
                isValid = false;
            }

            if (!/\d/.test(password)) {
                errors.push('Пароль должен содержать цифры');
                isValid = false;
            }
        }

        // Validate password match
        if (this.passwordInput && this.confirmPasswordInput &&
            this.passwordInput.value !== this.confirmPasswordInput.value) {
            errors.push('Пароли не совпадают');
            isValid = false;
            this.confirmPasswordInput.parentElement.classList.add('invalid');
        }

        // Validate terms
        if (this.termsCheckbox && !this.termsCheckbox.checked) {
            errors.push('Необходимо принять условия использования');
            isValid = false;
            this.validateTerms();
        }

        // Show errors
        if (errors.length > 0) {
            this.showErrorMessage(errors.join('. '));
        }

        return isValid;
    }

    async simulateLogin(username, password, remember) {
        // Simulate API request delay
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Demo logic - always succeed for demo purposes
                if (username && password) {
                    resolve({
                        success: true,
                        message: 'Добро пожаловать!',
                        user: {
                            username: username,
                            email: username.includes('@') ? username : `${username}@example.com`
                        }
                    });
                } else {
                    reject(new Error('Пожалуйста, заполните все поля'));
                }
            }, 1000);
        });
    }

    async simulateRegister() {
        // Simulate API request delay
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Demo logic - always succeed for demo purposes
                const email = this.emailInput.value;
                if (email && email.includes('@')) {
                    resolve({
                        success: true,
                        message: 'На вашу почту отправлено письмо с подтверждением',
                        user: {
                            email: email,
                            username: this.usernameInput.value
                        }
                    });
                } else {
                    reject(new Error('Пожалуйста, проверьте введенные данные'));
                }
            }, 1500);
        });
    }

    handleSocialAuth(e) {
        const provider = e.currentTarget.getAttribute('data-provider');
        const button = e.currentTarget;

        // Show loading state
        const originalContent = button.innerHTML;
        button.innerHTML = `<i class="fas fa-spinner fa-spin"></i> <span>Подключение...</span>`;
        button.disabled = true;

        // Simulate social auth
        setTimeout(() => {
            this.showInfoMessage(`Авторизация через ${provider} находится в разработке`);

            // Restore button
            button.innerHTML = originalContent;
            button.disabled = false;
        }, 1500);
    }

    handleRememberMe() {
        if (this.isRegisterPage) return;

        const rememberCheckbox = document.getElementById('auth-remember');
        const username = this.usernameInput.value.trim();

        if (rememberCheckbox.checked && username) {
            localStorage.setItem('auth_username', username);
            localStorage.setItem('auth_remember', 'true');
        } else if (!rememberCheckbox.checked) {
            localStorage.removeItem('auth_username');
            localStorage.removeItem('auth_remember');
        }
    }

    fillDemoData() {
        if (this.isRegisterPage) {
            // Already handled in setupDemoData
            return;
        }

        // Fill demo credentials for login
        this.usernameInput.value = 'demo_user';
        this.passwordInput.value = 'demo_password123';

        // Trigger validation
        this.validateInput(this.usernameInput);
        this.validateInput(this.passwordInput);

        // Show hint
        this.showInfoMessage('Демо данные заполнены. Нажмите "Войти" для продолжения.');
    }

    setLoadingState(isLoading) {
        if (isLoading) {
            this.submitButton.disabled = true;
            this.submitButton.classList.add('loading');

            const originalText = this.submitButton.querySelector('.auth-button-text');
            originalText.setAttribute('data-original-text', originalText.textContent);
            originalText.textContent = this.isRegisterPage ? 'Регистрация...' : 'Вход...';

            // Disable all inputs
            this.allInputs.forEach(input => {
                input.disabled = true;
            });

            // Disable password toggle buttons
            this.togglePasswordButtons.forEach(button => {
                button.disabled = true;
            });
        } else {
            this.submitButton.disabled = false;
            this.submitButton.classList.remove('loading');

            const originalText = this.submitButton.querySelector('.auth-button-text');
            const savedText = originalText.getAttribute('data-original-text');
            if (savedText) {
                originalText.textContent = savedText;
            }

            // Enable all inputs
            this.allInputs.forEach(input => {
                input.disabled = false;
            });

            // Enable password toggle buttons
            this.togglePasswordButtons.forEach(button => {
                button.disabled = false;
            });
        }
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const suffix = element.textContent.includes('%') ? '%' : '';
        const duration = 2000;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);

                // Dispatch event
                element.dispatchEvent(new CustomEvent('counterComplete', {
                    detail: { target, element }
                }));
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, stepTime);
    }

    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showInfoMessage(message) {
        this.showMessage(message, 'info');
    }

    showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.auth-message-toast');
        existingMessages.forEach(msg => msg.remove());

        // Create message element
        const messageElement = document.createElement('div');
        messageElement.className = `auth-message-toast auth-message-${type}`;
        messageElement.setAttribute('role', 'alert');
        messageElement.setAttribute('aria-live', 'polite');

        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            info: 'fa-info-circle',
            warning: 'fa-exclamation-triangle'
        };

        messageElement.innerHTML = `
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
            <button class="auth-message-close" aria-label="Закрыть">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add to DOM
        const formContent = document.querySelector('.auth-form-content');
        if (formContent) {
            formContent.appendChild(messageElement);
        } else {
            document.body.appendChild(messageElement);
        }

        // Add close functionality
        const closeButton = messageElement.querySelector('.auth-message-close');
        closeButton.addEventListener('click', () => {
            messageElement.classList.add('hiding');
            setTimeout(() => {
                messageElement.remove();
            }, 300);
        });

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (messageElement.parentNode) {
                messageElement.classList.add('hiding');
                setTimeout(() => {
                    if (messageElement.parentNode) {
                        messageElement.remove();
                    }
                }, 300);
            }
        }, 5000);
    }

    // Public methods
    focusUsername() {
        if (this.usernameInput) {
            this.usernameInput.focus();
        }
    }

    resetForm() {
        if (this.form) {
            this.form.reset();
        }

        // Clear validation states
        this.formGroups.forEach(group => {
            group.classList.remove('valid', 'invalid', 'focused');
        });
    }

    getFormData() {
        if (!this.form) return null;

        const formData = new FormData(this.form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        return data;
    }
}

// Initialize auth page
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on an auth page
    const loginForm = document.getElementById('auth-login-form');
    const registerForm = document.getElementById('auth-register-form');

    if (loginForm || registerForm) {
        window.AuthPage = new AuthPage();

        // Add CSS for message toasts if not already added
        if (!document.querySelector('#auth-message-styles')) {
            const styles = document.createElement('style');
            styles.id = 'auth-message-styles';
            styles.textContent = `
                .auth-message-toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: white;
                    border-radius: 16px;
                    padding: 16px 20px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    z-index: 10000;
                    max-width: 400px;
                    transform: translateX(100%);
                    opacity: 0;
                    transition: all 0.3s ease;
                    border: 1px solid rgba(0, 0, 0, 0.1);
                }

                .auth-message-toast.show {
                    transform: translateX(0);
                    opacity: 1;
                }

                .auth-message-toast.hiding {
                    transform: translateX(100%);
                    opacity: 0;
                }

                .auth-message-success {
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
                    border-color: rgba(16, 185, 129, 0.2);
                    color: #065f46;
                }

                .auth-message-error {
                    background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05));
                    border-color: rgba(239, 68, 68, 0.2);
                    color: #991b1b;
                }

                .auth-message-info {
                    background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
                    border-color: rgba(59, 130, 246, 0.2);
                    color: #1e40af;
                }

                .auth-message-warning {
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05));
                    border-color: rgba(245, 158, 11, 0.2);
                    color: #92400e;
                }

                .auth-message-toast i:first-child {
                    font-size: 18px;
                }

                .auth-message-toast span {
                    flex: 1;
                    font-weight: 600;
                    font-size: 14px;
                }

                .auth-message-close {
                    background: none;
                    border: none;
                    color: inherit;
                    cursor: pointer;
                    opacity: 0.7;
                    padding: 4px;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                }

                .auth-message-close:hover {
                    opacity: 1;
                    background: rgba(0, 0, 0, 0.1);
                }

                @media (max-width: 768px) {
                    .auth-message-toast {
                        left: 20px;
                        right: 20px;
                        max-width: none;
                    }
                }

                @media (prefers-color-scheme: dark) {
                    .auth-message-toast {
                        background: rgba(40, 40, 50, 0.95);
                        border-color: rgba(255, 255, 255, 0.1);
                    }

                    .auth-message-close:hover {
                        background: rgba(255, 255, 255, 0.1);
                    }
                }
            `;
            document.head.appendChild(styles);
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AuthPage };
}