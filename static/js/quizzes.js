// ===== QUIZZES PAGE FUNCTIONALITY =====

class QuizzesPage {
    constructor() {
        this.animatedElements = document.querySelectorAll('.quizzes-animate');
        this.progressBars = document.querySelectorAll('.quizzes-category-progress-bar');
        this.counters = document.querySelectorAll('[data-count]');
        this.searchInput = document.querySelector('.quizzes-search-input');
        this.quizCards = document.querySelectorAll('.quizzes-card');

        this.animationObserver = null;
        this.progressObserver = null;

        this.init();
    }

    init() {
        this.createParticles();
        this.setupAnimations();
        this.setupEventListeners();
        this.setupProgressBars();
        this.setupSearch();
        this.setupCounterAnimation();

        console.log('Quizzes page initialized 📝');
    }

    createParticles() {
        const particlesContainer = document.querySelector('.quizzes-hero-particles');
        if (!particlesContainer) return;

        const particleCount = 30;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'quizzes-particle';

            const size = Math.random() * 10 + 5;
            const left = Math.random() * 100;
            const delay = Math.random() * 20;
            const duration = Math.random() * 10 + 15;

            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${left}%`;
            particle.style.animationDelay = `${delay}s`;
            particle.style.animationDuration = `${duration}s`;

            particlesContainer.appendChild(particle);
        }
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
            this.animatedElements.forEach(element => {
                element.classList.add('animate-in');
            });
        }
    }

    setupProgressBars() {
        if ('IntersectionObserver' in window) {
            this.progressObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateProgressBar(entry.target);
                        this.progressObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -100px 0px'
            });

            this.progressBars.forEach(bar => {
                this.progressObserver.observe(bar);
            });
        } else {
            setTimeout(() => {
                this.progressBars.forEach(bar => {
                    this.animateProgressBar(bar);
                });
            }, 1000);
        }
    }

    animateProgressBar(bar) {
        const width = bar.getAttribute('data-width') || '70';
        const startTime = performance.now();
        const duration = 1500;

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const currentWidth = easeOutCubic * width;

            bar.style.width = `${currentWidth}%`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                bar.style.width = `${width}%`;

                bar.dispatchEvent(new CustomEvent('progressComplete', {
                    detail: { width, element: bar }
                }));
            }
        };

        requestAnimationFrame(animate);
    }

    setupCounterAnimation() {
        if ('IntersectionObserver' in window) {
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -100px 0px'
            });

            this.counters.forEach(counter => {
                counterObserver.observe(counter);
            });
        } else {
            setTimeout(() => {
                this.counters.forEach(counter => {
                    this.animateCounter(counter);
                });
            }, 1000);
        }
    }

    animateCounter(element) {
        const target = parseInt(element.getAttribute('data-count'));
        const suffix = element.textContent.includes('+') ? '+' : '';
        const duration = 1500;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, stepTime);
    }

    setupSearch() {
        if (!this.searchInput) return;

        const searchButton = document.querySelector('.quizzes-search-button');

        const performSearch = () => {
            const searchTerm = this.searchInput.value.toLowerCase().trim();

            if (searchTerm === '') {
                this.quizCards.forEach(card => {
                    card.style.display = 'block';
                });
                return;
            }

            this.quizCards.forEach(card => {
                const title = card.querySelector('.quizzes-card-title').textContent.toLowerCase();
                const category = card.querySelector('.quizzes-card-category').textContent.toLowerCase();
                const description = card.querySelector('.quizzes-card-description').textContent.toLowerCase();

                if (title.includes(searchTerm) || category.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                    card.classList.add('search-match');
                } else {
                    card.style.display = 'none';
                    card.classList.remove('search-match');
                }
            });
        };

        this.searchInput.addEventListener('input', performSearch);

        if (searchButton) {
            searchButton.addEventListener('click', performSearch);
        }

        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                performSearch();
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

        // Quiz card interaction
        this.quizCards.forEach(card => {
            const startBtn = card.querySelector('.quizzes-start-btn');

            startBtn?.addEventListener('click', (e) => {
                e.preventDefault();
                const quizId = card.getAttribute('data-quiz-id');
                this.startQuiz(quizId);
            });

            card.addEventListener('mouseenter', () => {
                card.classList.add('hover');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover');
            });
        });

        // Category card interaction
        document.querySelectorAll('.quizzes-category-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (!e.target.classList.contains('quizzes-category-card')) return;

                const category = card.getAttribute('data-category');
                this.filterByCategory(category);
            });
        });

        // Window resize handling
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        });
    }

    startQuiz(quizId) {
        console.log(`Starting quiz ${quizId}`);

        // Show loading state
        const startBtn = document.querySelector(`[data-quiz-id="${quizId}"] .quizzes-start-btn`);
        if (startBtn) {
            const originalText = startBtn.innerHTML;
            startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
            startBtn.disabled = true;

            // Simulate API call
            setTimeout(() => {
                // Redirect to quiz page
                window.location.href = `/quizzes/${quizId}/start/`;
            }, 500);
        }
    }

    filterByCategory(category) {
        console.log(`Filtering by category: ${category}`);

        this.quizCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');

            if (category === 'all' || cardCategory === category) {
                card.style.display = 'block';
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

    handleResize() {
        // Reset animations on resize
        this.animatedElements.forEach(element => {
            element.classList.remove('animate-in');
        });

        // Re-initialize animations
        setTimeout(() => {
            if (this.animationObserver) {
                this.animatedElements.forEach(element => {
                    this.animationObserver.observe(element);
                });
            }
        }, 100);
    }

    // Public methods
    triggerAnimations() {
        this.animatedElements.forEach(element => {
            element.classList.add('animate-in');
        });

        this.progressBars.forEach(bar => {
            this.animateProgressBar(bar);
        });

        this.counters.forEach(counter => {
            this.animateCounter(counter);
        });
    }

    resetAnimations() {
        this.animatedElements.forEach(element => {
            element.classList.remove('animate-in');
        });

        this.progressBars.forEach(bar => {
            bar.style.width = '0%';
        });

        this.counters.forEach(counter => {
            counter.textContent = '0';
        });

        if (this.animationObserver) {
            this.animatedElements.forEach(element => {
                this.animationObserver.observe(element);
            });
        }
    }
}

// Initialize quizzes page
document.addEventListener('DOMContentLoaded', () => {
    if ('fonts' in document) {
        document.fonts.ready.then(() => {
            window.QuizzesPage = new QuizzesPage();
        });
    } else {
        setTimeout(() => {
            window.QuizzesPage = new QuizzesPage();
        }, 1000);
    }
});

// Add custom event for quiz completion tracking
if (!document.querySelector('#quizzes-tracking')) {
    const script = document.createElement('script');
    script.id = 'quizzes-tracking';
    script.textContent = `
        document.addEventListener('quizStarted', (e) => {
            console.log('Quiz started:', e.detail);
            // Add analytics tracking here
        });

        document.addEventListener('quizCompleted', (e) => {
            console.log('Quiz completed:', e.detail);
            // Add analytics tracking here
        });
    `;
    document.head.appendChild(script);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { QuizzesPage };
}