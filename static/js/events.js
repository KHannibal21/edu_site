// ===== EVENTS PAGE FUNCTIONALITY =====

class EventsPage {
    constructor() {
        this.animatedElements = document.querySelectorAll('[data-animate]');
        this.counters = document.querySelectorAll('[data-count]');
        this.progressBars = document.querySelectorAll('.events-progress-fill');
        this.filterButtons = document.querySelectorAll('.events-filter-btn');
        this.eventCards = document.querySelectorAll('.events-card');
        this.registerButtons = document.querySelectorAll('.events-register-btn');
        this.subscribeButton = document.querySelector('.events-subscribe-btn');
        this.heroSearchButton = document.querySelector('.events-hero-search-button');
        this.heroUpcomingButtons = document.querySelectorAll('.events-hero-upcoming-button');
        this.animationObserver = null;
        this.counterObserver = null;

        this.init();
    }

    init() {
        this.setupAnimations();
        this.setupEventListeners();
        this.setupCounterAnimation();
        this.setupProgressBars();
        this.setupFiltering();

        console.log('Events page initialized 📅');
    }

    setupAnimations() {
        if ('IntersectionObserver' in window) {
            this.animationObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-in');
                        this.animationObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            this.animatedElements.forEach(element => {
                this.animationObserver.observe(element);
            });
        } else {
            // Fallback for browsers without IntersectionObserver
            this.animatedElements.forEach(element => {
                element.classList.add('animate-in');
            });
        }
    }

    setupCounterAnimation() {
        if ('IntersectionObserver' in window) {
            this.counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        this.counterObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -100px 0px'
            });

            this.counters.forEach(counter => {
                this.counterObserver.observe(counter);
            });
        } else {
            // Fallback: animate immediately
            setTimeout(() => {
                this.counters.forEach(counter => {
                    this.animateCounter(counter);
                });
            }, 1000);
        }
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const suffix = element.textContent.includes('%') ? '%' : '';
        const duration = 1500;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        element.classList.add('animating');

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);
                element.classList.remove('animating');

                element.dispatchEvent(new CustomEvent('counterComplete', {
                    detail: { target, element }
                }));
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, stepTime);
    }

    setupProgressBars() {
        if ('IntersectionObserver' in window) {
            const progressObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateProgressBar(entry.target);
                        progressObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -100px 0px'
            });

            this.progressBars.forEach(bar => {
                progressObserver.observe(bar);
            });
        } else {
            // Fallback: animate immediately
            setTimeout(() => {
                this.progressBars.forEach(bar => {
                    this.animateProgressBar(bar);
                });
            }, 1000);
        }
    }

    animateProgressBar(bar) {
        const width = bar.getAttribute('data-width');
        if (width) {
            const startTime = performance.now();
            const duration = 1500;

            bar.classList.add('animating');

            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                const currentWidth = easeOutQuart * width;

                bar.style.width = `${currentWidth}%`;

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    bar.style.width = `${width}%`;
                    bar.classList.remove('animating');

                    bar.dispatchEvent(new CustomEvent('progressComplete', {
                        detail: { width, element: bar }
                    }));
                }
            };

            requestAnimationFrame(animate);
        }
    }

    setupFiltering() {
        this.filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Remove active class from all buttons
                this.filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                button.classList.add('active');

                const filter = button.getAttribute('data-filter');
                this.filterEvents(filter);
            });
        });
    }

    filterEvents(filter) {
        this.eventCards.forEach(card => {
            const category = card.getAttribute('data-category');

            if (filter === 'all' || filter === category) {
                card.style.display = 'flex';
                setTimeout(() => {
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 100);
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.display = 'none';
                }, 300);
            }
        });
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const href = anchor.getAttribute('href');
                if (href !== '#') {
                    e.preventDefault();
                    const target = document.querySelector(href);
                    if (target) {
                        const headerHeight = document.querySelector('.header')?.offsetHeight || 80;
                        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                }
            });
        });

        // Register for event buttons
        this.registerButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const card = button.closest('.events-card');
                const eventTitle = card.querySelector('.events-card-title').textContent;

                this.showRegistrationModal(eventTitle);
            });
        });

        // Hero search button
        if (this.heroSearchButton) {
            this.heroSearchButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.performHeroSearch();
            });
        }

        // Hero upcoming event buttons
        this.heroUpcomingButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const eventCard = e.target.closest('.events-hero-upcoming-event');
                const eventTitle = eventCard.querySelector('h4').textContent;
                this.showRegistrationModal(eventTitle);
            });
        });

        // Subscribe button
        if (this.subscribeButton) {
            this.subscribeButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSubscriptionModal();
            });
        }

        // Card hover effects
        document.querySelectorAll('.events-card, .events-benefit-card, .events-past-card, .events-hero-stat-card, .events-hero-upcoming-event').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('hover');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover');
            });
        });

        // Improve select dropdowns in hero
        this.setupSelectStyles();

        // Handle window resize
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });

        // Handle page visibility
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.handleVisibilityChange();
            }
        });

        // Handle form submissions
        this.setupForms();
    }

    setupSelectStyles() {
        const selects = document.querySelectorAll('.events-hero-search-filter select');
        selects.forEach(select => {
            // Add custom styling for better visibility
            select.addEventListener('focus', () => {
                select.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
                select.style.borderColor = '#3b82f6';
            });

            select.addEventListener('blur', () => {
                select.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
                select.style.borderColor = 'rgba(255, 255, 255, 0.2)';
            });

            select.addEventListener('change', () => {
                select.style.color = '#ffffff';
            });
        });
    }

    setupForms() {
        // Handle search form
        const searchForm = document.querySelector('.events-hero-search-filters');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.performHeroSearch();
            });
        }
    }

    performHeroSearch() {
        const searchFilters = document.querySelectorAll('.events-hero-search-filter select');
        const filters = {};

        searchFilters.forEach(select => {
            const label = select.previousElementSibling.textContent.trim();
            filters[label] = select.value;
        });

        // Показываем уведомление
        this.showNotification('Ищем мероприятия по вашим критериям...', 'info');

        // Имитация поиска с анимацией
        setTimeout(() => {
            this.showNotification('Найдено 12 подходящих мероприятий!', 'success');

            // Прокрутка к результатам
            const upcomingSection = document.querySelector('#upcoming-events');
            if (upcomingSection) {
                const headerHeight = document.querySelector('.header')?.offsetHeight || 80;
                const targetPosition = upcomingSection.getBoundingClientRect().top + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });

                // Подсвечиваем секцию
                upcomingSection.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.3)';
                setTimeout(() => {
                    upcomingSection.style.boxShadow = '';
                }, 2000);
            }
        }, 1000);
    }

    showRegistrationModal(eventTitle) {
        // Check if modal already exists
        if (document.querySelector('.events-modal')) return;

        const modalHTML = `
            <div class="events-modal">
                <div class="events-modal-overlay"></div>
                <div class="events-modal-content">
                    <button class="events-modal-close">
                        <i class="fas fa-times"></i>
                    </button>

                    <h3>Регистрация на мероприятие</h3>
                    <p class="events-modal-subtitle">Вы регистрируетесь на: <strong>${eventTitle}</strong></p>

                    <form id="events-registration-form" class="events-modal-form">
                        <div class="events-form-group">
                            <label>Имя и фамилия *</label>
                            <input type="text" required placeholder="Введите ваше имя и фамилию">
                        </div>

                        <div class="events-form-group">
                            <label>Email *</label>
                            <input type="email" required placeholder="example@email.com">
                        </div>

                        <div class="events-form-group">
                            <label>Телефон</label>
                            <input type="tel" placeholder="+7 (777) 123-45-67">
                        </div>

                        <div class="events-form-group">
                            <label>Комментарий (опционально)</label>
                            <textarea placeholder="Ваши вопросы или пожелания" rows="3"></textarea>
                        </div>

                        <div class="events-form-checkbox">
                            <label>
                                <input type="checkbox" required>
                                <span>Я согласен на обработку персональных данных</span>
                            </label>
                        </div>

                        <div class="events-modal-buttons">
                            <button type="submit" class="btn btn-primary">
                                Подтвердить регистрацию
                            </button>
                            <button type="button" class="btn btn-outline events-modal-cancel">
                                Отмена
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer);

        // Add modal styles
        const style = document.createElement('style');
        style.textContent = `
            .events-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 1000;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                animation: eventsModalFadeIn 0.3s ease;
            }

            .events-modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }

            .events-modal-content {
                position: relative;
                background: white;
                padding: 40px;
                border-radius: 24px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                z-index: 1001;
                animation: eventsModalSlideIn 0.3s ease;
                max-height: 90vh;
                overflow-y: auto;
            }

            .events-modal-close {
                position: absolute;
                top: 20px;
                right: 20px;
                background: none;
                border: none;
                font-size: 24px;
                color: #64748b;
                cursor: pointer;
                padding: 5px;
                line-height: 1;
                transition: color 0.3s ease;
            }

            .events-modal-close:hover {
                color: #ef4444;
            }

            .events-modal-content h3 {
                font-size: 24px;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 10px;
            }

            .events-modal-subtitle {
                color: #64748b;
                margin-bottom: 30px;
                line-height: 1.5;
            }

            .events-modal-form {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }

            .events-form-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }

            .events-form-group label {
                font-weight: 600;
                color: #1e293b;
                font-size: 14px;
            }

            .events-form-group input,
            .events-form-group textarea {
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 16px;
                transition: all 0.3s ease;
                font-family: inherit;
            }

            .events-form-group input:focus,
            .events-form-group textarea:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }

            .events-form-checkbox {
                display: flex;
                align-items: flex-start;
                gap: 10px;
                font-size: 14px;
                color: #64748b;
            }

            .events-form-checkbox input[type="checkbox"] {
                width: 18px;
                height: 18px;
                margin-top: 2px;
                cursor: pointer;
            }

            .events-modal-buttons {
                display: flex;
                gap: 15px;
                margin-top: 10px;
            }

            .events-modal-buttons .btn {
                flex: 1;
                justify-content: center;
            }

            @keyframes eventsModalFadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes eventsModalSlideIn {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes eventsModalFadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }

            @keyframes eventsModalSlideOut {
                from {
                    opacity: 1;
                    transform: translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateY(-20px);
                }
            }

            @media (max-width: 640px) {
                .events-modal-content {
                    padding: 30px 20px;
                }

                .events-modal-buttons {
                    flex-direction: column;
                }
            }

            @media (prefers-color-scheme: dark) {
                .events-modal-content {
                    background: #1e293b;
                    color: #e2e8f0;
                }

                .events-modal-content h3 {
                    color: #ffffff;
                }

                .events-modal-subtitle {
                    color: #94a3b8;
                }

                .events-form-group label {
                    color: #e2e8f0;
                }

                .events-form-group input,
                .events-form-group textarea {
                    background: #0f172a;
                    border-color: #334155;
                    color: #e2e8f0;
                }

                .events-form-group input:focus,
                .events-form-group textarea:focus {
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
                }

                .events-form-checkbox {
                    color: #94a3b8;
                }
            }
        `;
        document.head.appendChild(style);

        // Form submission
        const form = modalContainer.querySelector('#events-registration-form');
        const closeBtn = modalContainer.querySelector('.events-modal-close');
        const cancelBtn = modalContainer.querySelector('.events-modal-cancel');
        const modal = modalContainer.querySelector('.events-modal');
        const modalContent = modalContainer.querySelector('.events-modal-content');

        const closeModal = () => {
            modal.style.animation = 'eventsModalFadeOut 0.3s ease';
            modalContent.style.animation = 'eventsModalSlideOut 0.3s ease';

            setTimeout(() => {
                if (modalContainer.parentNode) {
                    document.body.removeChild(modalContainer);
                }
                document.head.removeChild(style);
            }, 300);
        };

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Валидация формы
            const inputs = form.querySelectorAll('input[required]');
            let isValid = true;

            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.style.borderColor = '#ef4444';
                    isValid = false;
                } else {
                    input.style.borderColor = '#10b981';
                }
            });

            if (!isValid) {
                this.showNotification('Пожалуйста, заполните все обязательные поля', 'error');
                return;
            }

            // Анимация закрытия
            modal.style.animation = 'eventsModalFadeOut 0.3s ease';
            modalContent.style.animation = 'eventsModalSlideOut 0.3s ease';

            setTimeout(() => {
                this.showNotification('Регистрация успешно завершена! На вашу почту отправлено подтверждение.', 'success');
                closeModal();
            }, 300);
        });

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('events-modal-overlay')) {
                closeModal();
            }
        });

        // Focus on first input
        setTimeout(() => {
            const firstInput = form.querySelector('input');
            if (firstInput) firstInput.focus();
        }, 100);

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Restore scroll when modal closes
        const restoreScroll = () => {
            document.body.style.overflow = '';
        };

        modal.addEventListener('animationend', (e) => {
            if (e.animationName === 'eventsModalFadeOut') {
                restoreScroll();
            }
        });

        closeBtn.addEventListener('click', restoreScroll);
        cancelBtn.addEventListener('click', restoreScroll);
    }

    showSubscriptionModal() {
        // Check if modal already exists
        if (document.querySelector('.events-modal')) return;

        const modalHTML = `
            <div class="events-modal">
                <div class="events-modal-overlay"></div>
                <div class="events-modal-content">
                    <button class="events-modal-close">
                        <i class="fas fa-times"></i>
                    </button>

                    <h3>Подписка на анонсы</h3>
                    <p class="events-modal-subtitle">Будьте первыми, кто узнает о новых мероприятиях и специальных предложениях!</p>

                    <form id="events-subscription-form" class="events-modal-form">
                        <div class="events-form-group">
                            <label>Email *</label>
                            <input type="email" required placeholder="ваш@email.com">
                        </div>

                        <div class="events-form-group">
                            <label>Имя</label>
                            <input type="text" placeholder="Как к вам обращаться?">
                        </div>

                        <div class="events-form-checkbox">
                            <label>
                                <input type="checkbox" required>
                                <span>Я согласен получать информацию о мероприятиях и специальных предложениях</span>
                            </label>
                        </div>

                        <div class="events-form-checkbox">
                            <label>
                                <input type="checkbox">
                                <span>Хочу получать уведомления о мероприятиях по интересам</span>
                            </label>
                        </div>

                        <div class="events-modal-buttons">
                            <button type="submit" class="btn btn-primary">
                                <i class="fas fa-bell"></i>
                                Подписаться
                            </button>
                            <button type="button" class="btn btn-outline events-modal-cancel">
                                Отмена
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHTML;
        document.body.appendChild(modalContainer);

        // Form submission
        const form = modalContainer.querySelector('#events-subscription-form');
        const closeBtn = modalContainer.querySelector('.events-modal-close');
        const cancelBtn = modalContainer.querySelector('.events-modal-cancel');
        const modal = modalContainer.querySelector('.events-modal');
        const modalContent = modalContainer.querySelector('.events-modal-content');

        const closeModal = () => {
            modal.style.animation = 'eventsModalFadeOut 0.3s ease';
            modalContent.style.animation = 'eventsModalSlideOut 0.3s ease';

            setTimeout(() => {
                if (modalContainer.parentNode) {
                    document.body.removeChild(modalContainer);
                }
                document.body.style.overflow = '';
            }, 300);
        };

        form.addEventListener('submit', (e) => {
            e.preventDefault();

            // Валидация email
            const emailInput = form.querySelector('input[type="email"]');
            const email = emailInput.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!emailRegex.test(email)) {
                emailInput.style.borderColor = '#ef4444';
                this.showNotification('Пожалуйста, введите корректный email адрес', 'error');
                return;
            }

            // Анимация закрытия
            modal.style.animation = 'eventsModalFadeOut 0.3s ease';
            modalContent.style.animation = 'eventsModalSlideOut 0.3s ease';

            setTimeout(() => {
                this.showNotification('Вы успешно подписались на анонсы мероприятий!', 'success');
                closeModal();
            }, 300);
        });

        closeBtn.addEventListener('click', closeModal);
        cancelBtn.addEventListener('click', closeModal);

        modal.addEventListener('click', (e) => {
            if (e.target === modal || e.target.classList.contains('events-modal-overlay')) {
                closeModal();
            }
        });

        // Focus on email input
        setTimeout(() => {
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput) emailInput.focus();
        }, 100);

        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.querySelector('.events-notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const icon = type === 'success' ? 'check-circle' :
                    type === 'error' ? 'exclamation-circle' :
                    'info-circle';

        const backgroundColor = type === 'success' ? '#10b981' :
                              type === 'error' ? '#ef4444' :
                              '#3b82f6';

        const notification = document.createElement('div');
        notification.className = `events-notification events-notification-${type}`;
        notification.innerHTML = `
            <div class="events-notification-content">
                <i class="fas fa-${icon}"></i>
                <span>${message}</span>
            </div>
        `;

        // Стили для уведомления
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${backgroundColor};
            color: white;
            padding: 15px 25px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            z-index: 1001;
            animation: eventsNotificationSlideIn 0.3s ease;
            max-width: 400px;
            word-wrap: break-word;
        `;

        document.body.appendChild(notification);

        // Добавляем стили для анимации
        if (!document.querySelector('#events-notification-styles')) {
            const styles = document.createElement('style');
            styles.id = 'events-notification-styles';
            styles.textContent = `
                @keyframes eventsNotificationSlideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                @keyframes eventsNotificationSlideOut {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }

                .events-notification-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    font-weight: 600;
                }

                .events-notification-content i {
                    font-size: 18px;
                    flex-shrink: 0;
                }
            `;
            document.head.appendChild(styles);
        }

        // Удаляем уведомление через 3 секунды
        setTimeout(() => {
            notification.style.animation = 'eventsNotificationSlideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    handleResize() {
        // Reset animations on resize
        this.animatedElements.forEach(element => {
            element.classList.remove('animate-in');
        });

        // Re-initialize animations after a short delay
        setTimeout(() => {
            if (this.animationObserver) {
                this.animatedElements.forEach(element => {
                    this.animationObserver.observe(element);
                });
            }
        }, 100);
    }

    handleVisibilityChange() {
        // Resume counter animations if they were interrupted
        this.counters.forEach(counter => {
            if (!counter.textContent.includes(counter.getAttribute('data-count'))) {
                this.animateCounter(counter);
            }
        });
    }

    // Public method to trigger animations manually
    triggerAnimations() {
        this.animatedElements.forEach(element => {
            element.classList.add('animate-in');
        });

        this.counters.forEach(counter => {
            this.animateCounter(counter);
        });

        this.progressBars.forEach(bar => {
            this.animateProgressBar(bar);
        });
    }

    // Public method to reset animations
    resetAnimations() {
        this.animatedElements.forEach(element => {
            element.classList.remove('animate-in');
        });

        this.counters.forEach(counter => {
            counter.textContent = '0';
            if (counter.getAttribute('data-count').includes('%')) {
                counter.textContent = '0%';
            }
        });

        this.progressBars.forEach(bar => {
            bar.style.width = '0%';
        });

        if (this.animationObserver) {
            this.animatedElements.forEach(element => {
                this.animationObserver.observe(element);
            });
        }
    }
}

// Initialize events page
document.addEventListener('DOMContentLoaded', () => {
    // Wait for fonts to load
    if ('fonts' in document) {
        document.fonts.ready.then(() => {
            window.EventsPage = new EventsPage();
        });
    } else {
        // Fallback for browsers without Font Loading API
        setTimeout(() => {
            window.EventsPage = new EventsPage();
        }, 1000);
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { EventsPage };
}