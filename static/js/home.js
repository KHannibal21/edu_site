// ===== HOME PAGE FUNCTIONALITY =====

class HomePage {
    constructor() {
        this.animatedElements = document.querySelectorAll('[data-animate]');
        this.counters = document.querySelectorAll('[data-count]');
        this.progressBars = document.querySelectorAll('.home-progress-fill');
        this.animationObserver = null;
        this.counterObserver = null;

        this.init();
    }

    init() {
        this.setupAnimations();
        this.setupEventListeners();
        this.setupCounterAnimation();
        this.setupProgressBars();

        console.log('Home page initialized 🏠');
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
        const duration = 1500; // 1.5 seconds
        const stepTime = 16; // ~60fps
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);

                // Dispatch custom event
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
            // Use requestAnimationFrame for smooth animation
            const startTime = performance.now();
            const duration = 1500; // 1.5 seconds

            const animate = (currentTime) => {
                const elapsed = currentTime - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Easing function for smooth animation
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                const currentWidth = easeOutQuart * width;

                bar.style.width = `${currentWidth}%`;

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    bar.style.width = `${width}%`;

                    // Dispatch custom event
                    bar.dispatchEvent(new CustomEvent('progressComplete', {
                        detail: { width, element: bar }
                    }));
                }
            };

            requestAnimationFrame(animate);
        }
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

        // Card hover effects
        document.querySelectorAll('.home-course-card, .home-advantage-card, .home-testimonial-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('hover');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover');
            });
        });

        // Feature blocks interaction
        document.querySelectorAll('.home-feature-block').forEach(block => {
            block.addEventListener('click', () => {
                block.classList.toggle('active');
            });
        });

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
            if (counter.textContent.includes('%')) {
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

// Initialize home page
document.addEventListener('DOMContentLoaded', () => {
    // Wait for fonts to load
    if ('fonts' in document) {
        document.fonts.ready.then(() => {
            window.HomePage = new HomePage();
        });
    } else {
        // Fallback for browsers without Font Loading API
        setTimeout(() => {
            window.HomePage = new HomePage();
        }, 1000);
    }
});

// Add CSS animations for counter and progress bar
if (!document.querySelector('#home-animation-styles')) {
    const styles = document.createElement('style');
    styles.id = 'home-animation-styles';
    styles.textContent = `
        @keyframes home-counter-pop {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .home-hero-stat-number.animating {
            animation: home-counter-pop 0.3s ease;
        }

        @keyframes home-progress-glow {
            0% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
            50% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.8); }
            100% { box-shadow: 0 0 5px rgba(102, 126, 234, 0.5); }
        }

        .home-progress-fill.animating {
            animation: home-progress-glow 2s ease-in-out infinite;
        }
    `;
    document.head.appendChild(styles);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { HomePage };
}