// ===== EDUPLATFORM MAIN JS =====
// Modern, modular JavaScript with enhanced functionality

class EduPlatform {
    constructor() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth <= 1024;
        this.scrollPosition = 0;
        this.init();
    }

    init() {
        this.setupGlobals();
        this.bindGlobalEvents();
        this.setupAccessibility();
        this.setupPerformance();
        this.setupUIComponents();

        console.log('EduPlatform initialized 🚀');
    }

    setupGlobals() {
        // Global utility methods
        window.eduPlatform = this;
        window.eduUtils = this.utils;
    }

    bindGlobalEvents() {
        // Handle focus for accessibility
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });

        // Handle viewport changes
        window.addEventListener('resize', this.debounce(() => {
            this.handleViewportChange();
        }, 250));

        // Handle page visibility
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });

        // Handle beforeunload for form submissions
        window.addEventListener('beforeunload', (e) => {
            this.handleBeforeUnload(e);
        });
    }

    setupAccessibility() {
        // Убрали addSkipLink() - больше не создаем skip-link
        this.setupFocusManagement();
        this.setupLiveRegions();
        this.setupReducedMotion();
    }

    setupPerformance() {
        this.setupLazyLoading();
        this.preloadCriticalResources();
        this.setupIntersectionObservers();
    }

    setupUIComponents() {
        this.setupLoadingStates();
        this.setupProgressBars();
        this.setupCounters();
    }

    // ===== ACCESSIBILITY METHODS =====
    // Убрали метод addSkipLink() полностью

    setupFocusManagement() {
        // Trap focus in modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }

    setupLiveRegions() {
        // Create live region for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.id = 'a11y-live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        document.body.appendChild(liveRegion);
    }

    setupReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('reduced-motion');
        }
    }

    // ===== PERFORMANCE METHODS =====
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const lazyObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;

                        if (element.dataset.src) {
                            element.src = element.dataset.src;
                            element.removeAttribute('data-src');
                        }

                        if (element.dataset.srcset) {
                            element.srcset = element.dataset.srcset;
                            element.removeAttribute('data-srcset');
                        }

                        if (element.dataset.bg) {
                            element.style.backgroundImage = `url(${element.dataset.bg})`;
                            element.removeAttribute('data-bg');
                        }

                        element.classList.remove('lazy');
                        lazyObserver.unobserve(element);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.1
            });

            document.querySelectorAll('[data-src], [data-srcset], [data-bg]').forEach(el => {
                lazyObserver.observe(el);
            });
        }
    }

    preloadCriticalResources() {
        const critical = [
            // Add critical resources here
        ];

        critical.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource.url;
            link.as = resource.type;
            if (resource.crossorigin) link.crossOrigin = 'anonymous';
            document.head.appendChild(link);
        });
    }

    setupIntersectionObservers() {
        // Animate elements on scroll
        if ('IntersectionObserver' in window) {
            const animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        animationObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            document.querySelectorAll('[data-animate]').forEach(el => {
                animationObserver.observe(el);
            });
        }
    }

    // ===== UI COMPONENTS =====
    setupLoadingStates() {
        // Add loading states to buttons and forms
        document.addEventListener('submit', (e) => {
            const form = e.target;
            const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');

            if (submitBtn) {
                this.setLoadingState(submitBtn, true);

                // Reset loading state after form submission
                form.addEventListener('ajax:complete', () => {
                    this.setLoadingState(submitBtn, false);
                });
            }
        });
    }

    setupProgressBars() {
        // Initialize progress bars
        document.querySelectorAll('.progress-bar').forEach(bar => {
            const value = bar.dataset.value || 0;
            this.animateProgressBar(bar, value);
        });
    }

    setupCounters() {
        // Animate number counters
        document.querySelectorAll('[data-counter]').forEach(counter => {
            const target = parseInt(counter.dataset.counter);
            const duration = parseInt(counter.dataset.duration) || 2000;
            this.animateCounter(counter, target, duration);
        });
    }

    // ===== UTILITY METHODS =====
    debounce(func, wait, immediate = false) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    setLoadingState(element, isLoading) {
        if (isLoading) {
            element.disabled = true;
            element.setAttribute('aria-busy', 'true');
            element.classList.add('loading');

            const originalText = element.innerHTML;
            element.setAttribute('data-original-text', originalText);
            element.innerHTML = '<span class="loading-spinner"></span> Загрузка...';
        } else {
            element.disabled = false;
            element.removeAttribute('aria-busy');
            element.classList.remove('loading');

            const originalText = element.getAttribute('data-original-text');
            if (originalText) {
                element.innerHTML = originalText;
            }
        }
    }

    animateProgressBar(bar, targetValue, duration = 1000) {
        const startValue = 0;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const currentValue = startValue + (targetValue - startValue) * progress;
            bar.style.width = `${currentValue}%`;
            bar.setAttribute('aria-valuenow', Math.round(currentValue));

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    animateCounter(element, target, duration = 2000) {
        const start = 0;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            // Easing function
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = Math.floor(start + (target - start) * easeOutQuart);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = target.toLocaleString();
            }
        };

        requestAnimationFrame(animate);
    }

    // ===== NOTIFICATION SYSTEM =====
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');

        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };

        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${icons[type] || icons.info}</span>
                <span class="notification-message">${message}</span>
            </div>
            <button class="notification-close" aria-label="Закрыть уведомление">
                <span aria-hidden="true">×</span>
            </button>
        `;

        document.body.appendChild(notification);

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Close button
        notification.querySelector('.notification-close').addEventListener('click', () => {
            this.hideNotification(notification);
        });

        // Auto hide
        if (duration > 0) {
            setTimeout(() => {
                this.hideNotification(notification);
            }, duration);
        }

        return notification;
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        notification.classList.add('hide');

        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }

    // ===== EVENT HANDLERS =====
    handleViewportChange() {
        this.isMobile = window.innerWidth <= 768;
        this.isTablet = window.innerWidth <= 1024;

        // Dispatch custom event
        window.dispatchEvent(new CustomEvent('viewportchange', {
            detail: {
                isMobile: this.isMobile,
                isTablet: this.isTablet,
                width: window.innerWidth
            }
        }));
    }

    handleVisibilityChange() {
        if (document.hidden) {
            document.body.classList.add('page-hidden');
        } else {
            document.body.classList.remove('page-hidden');
        }
    }

    handleBeforeUnload(e) {
        // Check for unsaved forms
        const unsavedForms = document.querySelectorAll('form[data-unsaved]');
        if (unsavedForms.length > 0) {
            e.preventDefault();
            e.returnValue = 'У вас есть несохраненные изменения. Вы уверены, что хотите уйти?';
            return e.returnValue;
        }
    }

    closeAllModals() {
        // Close all open modals, dropdowns, etc.
        document.querySelectorAll('.modal.show, .dropdown-menu.show').forEach(el => {
            el.classList.remove('show');
        });

        document.querySelectorAll('[aria-expanded="true"]').forEach(el => {
            el.setAttribute('aria-expanded', 'false');
        });
    }

    // ===== PUBLIC API =====
    get utils() {
        return {
            formatDate: (date) => {
                return new Date(date).toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            },

            formatTime: (date) => {
                return new Date(date).toLocaleTimeString('ru-RU', {
                    hour: '2-digit',
                    minute: '2-digit'
                });
            },

            truncateText: (text, length) => {
                if (text.length <= length) return text;
                return text.substring(0, length).trim() + '...';
            },

            generateId: (prefix = '') => {
                return prefix + Date.now().toString(36) + Math.random().toString(36).substr(2);
            },

            isInViewport: (element) => {
                const rect = element.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                    rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                );
            },

            getScrollPosition: () => {
                return window.pageYOffset || document.documentElement.scrollTop;
            },

            scrollToElement: (element, offset = 0) => {
                const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = elementPosition - offset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        };
    }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    // Initialize main platform
    window.EduPlatform = new EduPlatform();

    // Add CSS for notifications
    if (!document.querySelector('#notification-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: var(--bg-primary);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-lg);
                padding: var(--space-4);
                box-shadow: var(--shadow-2xl);
                max-width: 400px;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s ease;
                z-index: 10000;
                display: flex;
                align-items: center;
                gap: var(--space-3);
            }

            .notification.show {
                transform: translateX(0);
                opacity: 1;
            }

            .notification.hide {
                transform: translateX(100%);
                opacity: 0;
            }

            .notification-content {
                display: flex;
                align-items: center;
                gap: var(--space-3);
                flex: 1;
            }

            .notification-close {
                background: none;
                border: none;
                cursor: pointer;
                padding: var(--space-1);
                border-radius: var(--radius-sm);
                color: var(--text-secondary);
                transition: var(--transition-base);
                font-size: 1.2em;
            }

            .notification-close:hover {
                background: var(--bg-secondary);
                color: var(--text-primary);
            }

            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }

            @media (max-width: 768px) {
                .notification {
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
            }
        `;
        document.head.appendChild(styles);
    }
});

// ===== GLOBAL EXPORTS =====
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EduPlatform };
}