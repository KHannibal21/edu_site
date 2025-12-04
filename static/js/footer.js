// ===== FOOTER FUNCTIONALITY =====

class Footer {
    constructor() {
        this.footer = document.querySelector('.footer');
        this.newsletterForm = document.querySelector('.newsletter-form');
        this.socialLinks = document.querySelectorAll('.social-link');
        this.footerLinks = document.querySelectorAll('.footer-link, .footer-bottom-link');

        this.init();
    }

    init() {
        this.bindEvents();
        this.setupScrollAnimations();
        this.setupHoverEffects();

        console.log('Footer initialized 📄');
    }

    bindEvents() {
        // Newsletter form submission
        if (this.newsletterForm) {
            this.newsletterForm.addEventListener('submit', (e) => {
                this.handleNewsletterSubmit(e);
            });
        }

        // Track social link clicks
        this.setupSocialTracking();
    }

    handleNewsletterSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const input = form.querySelector('.newsletter-input');
        const button = form.querySelector('.newsletter-button');
        const successMessage = document.getElementById('newsletter-success');
        const email = input.value.trim();

        // Validation
        if (!this.isValidEmail(email)) {
            this.showNewsletterError('Пожалуйста, введите корректный email', input);
            return;
        }

        // Disable form during submission
        this.setNewsletterState(button, true, 'Отправка...');

        // Simulate API call
        this.subscribeToNewsletter(email)
            .then(() => {
                this.showNewsletterSuccess(successMessage);
                input.value = '';

                // Reset form state after success
                setTimeout(() => {
                    if (successMessage) {
                        successMessage.style.display = 'none';
                    }
                }, 3000);
            })
            .catch(error => {
                this.showNewsletterError(error.message, input);
            })
            .finally(() => {
                this.setNewsletterState(button, false, 'Подписаться');
            });
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    setNewsletterState(button, isLoading, text) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + text;
            button.classList.add('loading');
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane"></i> ' + text;
            button.classList.remove('loading');
        }
    }

    async subscribeToNewsletter(email) {
        // Simulate API request with realistic delay
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Simulate 90% success rate
                if (Math.random() < 0.9) {
                    resolve({
                        success: true,
                        message: 'Вы успешно подписались на рассылку!'
                    });
                } else {
                    // Simulate different error scenarios
                    const errors = [
                        'Сервер временно недоступен. Попробуйте позже.',
                        'Превышен лимит запросов. Попробуйте через несколько минут.',
                        'Произошла ошибка подключения.'
                    ];
                    reject(new Error(errors[Math.floor(Math.random() * errors.length)]));
                }
            }, 1500);
        });
    }

    showNewsletterSuccess(successElement) {
        if (successElement) {
            successElement.style.display = 'flex';
            successElement.style.animation = 'slideDown 0.3s ease';
        }

        // Show global notification if available
        if (window.EduPlatform) {
            window.EduPlatform.showNotification('Вы успешно подписались на рассылку!', 'success', 3000);
        }
    }

    showNewsletterError(message, input) {
        // Add visual error state to input
        if (input) {
            input.classList.add('error');
            input.style.borderColor = '#ef4444';

            // Create error message element
            const errorElement = document.createElement('div');
            errorElement.className = 'newsletter-error';
            errorElement.style.color = '#ef4444';
            errorElement.style.fontSize = '13px';
            errorElement.style.marginTop = '8px';
            errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

            // Remove existing error if present
            const existingError = input.parentElement.querySelector('.newsletter-error');
            if (existingError) {
                existingError.remove();
            }

            input.parentElement.appendChild(errorElement);

            // Remove error state after 3 seconds
            setTimeout(() => {
                input.classList.remove('error');
                input.style.borderColor = '';
                if (errorElement.parentElement) {
                    errorElement.remove();
                }
            }, 3000);
        }

        // Show global notification if available
        if (window.EduPlatform) {
            window.EduPlatform.showNotification(message, 'error', 3000);
        }
    }

    setupSocialTracking() {
        this.socialLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const platform = link.querySelector('.social-text')?.textContent ||
                                link.getAttribute('aria-label') ||
                                'Unknown Platform';
                this.trackSocialClick(platform, link.href);
            });
        });
    }

    trackSocialClick(platform, url) {
        // Analytics tracking
        console.log(`Social link clicked: ${platform} - ${url}`);

        // You can integrate with actual analytics here
        if (typeof gtag !== 'undefined') {
            gtag('event', 'social_click', {
                'event_category': 'Social',
                'event_label': platform,
                'transport_type': 'beacon'
            });
        }
    }

    setupScrollAnimations() {
        // Animate footer elements on scroll
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // Observe footer sections
            document.querySelectorAll('.footer-section').forEach(section => {
                observer.observe(section);
            });
        }
    }

    setupHoverEffects() {
        // Add ripple effect to buttons
        this.footerLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.classList.add('hover');
            });

            link.addEventListener('mouseleave', () => {
                link.classList.remove('hover');
            });
        });
    }

    // Public method to update footer year
    updateCurrentYear() {
        const yearElement = document.querySelector('.copyright');
        if (yearElement) {
            const currentYear = new Date().getFullYear();
            yearElement.innerHTML = yearElement.innerHTML.replace(/2024/, currentYear);
        }
    }

    // Public method to update newsletter form
    updateNewsletterPlaceholder(placeholder) {
        const input = this.newsletterForm?.querySelector('.newsletter-input');
        if (input) {
            input.placeholder = placeholder;
        }
    }
}

// Initialize footer
document.addEventListener('DOMContentLoaded', () => {
    const footer = new Footer();

    // Update current year automatically
    footer.updateCurrentYear();

    // Export footer instance globally
    window.Footer = footer;

    console.log('Footer initialized successfully 🎉');
});

// Add CSS for loading spinner
if (!document.querySelector('#footer-styles')) {
    const styles = document.createElement('style');
    styles.id = 'footer-styles';
    styles.textContent = `
        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .footer-section.animate-in {
            animation: fadeInUp 0.5s ease forwards;
        }

        .footer-section:nth-child(1) { animation-delay: 0.1s; }
        .footer-section:nth-child(2) { animation-delay: 0.2s; }
        .footer-section:nth-child(3) { animation-delay: 0.3s; }
        .footer-section:nth-child(4) { animation-delay: 0.4s; }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .newsletter-error {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            margin-top: 8px;
            animation: slideDown 0.3s ease;
        }
    `;
    document.head.appendChild(styles);
}