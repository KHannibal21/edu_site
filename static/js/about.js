// ===== ABOUT PAGE FUNCTIONALITY =====

class AboutPage {
    constructor() {
        this.animatedElements = document.querySelectorAll('[data-animate]');
        this.counters = document.querySelectorAll('[data-count]');
        this.animationObserver = null;
        this.counterObserver = null;

        this.init();
    }

    init() {
        this.setupAnimations();
        this.setupEventListeners();
        this.setupCounterAnimation();

        console.log('About page initialized ℹ️');
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
        const duration = 2000; // 2 seconds
        const stepTime = 16; // ~60fps
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        // Add animating class
        element.classList.add('animating');

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = target + suffix;
                clearInterval(timer);
                element.classList.remove('animating');

                // Dispatch custom event
                element.dispatchEvent(new CustomEvent('counterComplete', {
                    detail: { target, element }
                }));
            } else {
                element.textContent = Math.floor(current) + suffix;
            }
        }, stepTime);
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
        document.querySelectorAll('.about-mission-card, .about-advantage-item, .about-team-member, .about-stat-item').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.classList.add('hover');
            });

            card.addEventListener('mouseleave', () => {
                card.classList.remove('hover');
            });
        });

        // Mission card interaction
        document.querySelectorAll('.about-mission-card').forEach(card => {
            card.addEventListener('click', () => {
                card.classList.toggle('active');
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

        // Team member interaction
        document.querySelectorAll('.about-team-member').forEach(member => {
            member.addEventListener('click', () => {
                this.showTeamMemberDetail(member);
            });
        });
    }

    showTeamMemberDetail(member) {
        const name = member.querySelector('h3').textContent;
        const role = member.querySelector('.about-team-member-role').textContent;
        const bio = member.querySelector('.about-team-member-bio').textContent;

        // You could implement a modal or expandable detail view here
        // For now, just log the information
        console.log(`Team Member: ${name}, ${role}`);
        console.log(`Bio: ${bio}`);

        // Show notification
        if (window.EduPlatform) {
            window.EduPlatform.showNotification(`Подробнее о ${name}`, 'info', 3000);
        }
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

        if (this.animationObserver) {
            this.animatedElements.forEach(element => {
                this.animationObserver.observe(element);
            });
        }
    }

    // Public method to get statistics
    getStatistics() {
        const stats = {};
        this.counters.forEach(counter => {
            const label = counter.nextElementSibling?.textContent || 'Unknown';
            stats[label] = {
                target: parseInt(counter.getAttribute('data-count')),
                current: parseInt(counter.textContent) || 0
            };
        });
        return stats;
    }
}

// Initialize about page
document.addEventListener('DOMContentLoaded', () => {
    // Wait for fonts to load
    if ('fonts' in document) {
        document.fonts.ready.then(() => {
            window.AboutPage = new AboutPage();
        });
    } else {
        // Fallback for browsers without Font Loading API
        setTimeout(() => {
            window.AboutPage = new AboutPage();
        }, 1000);
    }
});

// Add CSS animations for counter
if (!document.querySelector('#about-animation-styles')) {
    const styles = document.createElement('style');
    styles.id = 'about-animation-styles';
    styles.textContent = `
        @keyframes about-counter-pop {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }

        .about-stat-number.animating,
        .about-hero-stat-number.animating {
            animation: about-counter-pop 0.3s ease;
        }

        @keyframes about-shape-float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-20px) rotate(180deg); }
        }

        .about-hero-shape,
        .about-stats-shape,
        .about-cta-shape {
            animation: about-shape-float 20s ease-in-out infinite;
        }

        @keyframes about-card-float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-5px); }
        }

        .about-mission-card.hover,
        .about-advantage-item.hover,
        .about-team-member.hover {
            animation: about-card-float 3s ease-in-out infinite;
        }
    `;
    document.head.appendChild(styles);
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AboutPage };
}