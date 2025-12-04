// ===== NAVIGATION FUNCTIONALITY =====

class Navigation {
    constructor() {
        this.navbar = document.querySelector('.navbar');
        this.navMenu = document.querySelector('.nav-menu');
        this.navItems = document.querySelectorAll('.nav-item');
        this.navLinks = document.querySelectorAll('.nav-link');

        this.isMobile = window.innerWidth <= 768;
        this.scrollDirection = 'up';
        this.lastScrollY = window.pageYOffset;
        this.scrollThreshold = 100;

        this.init();
    }

    init() {
        this.bindEvents();
        this.handleScroll();
        this.handleResize();
        this.setupScrollIndicators();
        this.setupActiveStates();

        console.log('Navigation initialized 🧭');
    }

    bindEvents() {
        // Handle nav item hover effects
        this.setupHoverEffects();

        // Handle keyboard navigation
        this.setupKeyboardNavigation();
    }

    setupHoverEffects() {
        if (this.isMobile) return;

        this.navItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                this.navItems.forEach(i => i.classList.remove('hover'));
                item.classList.add('hover');
            });

            item.addEventListener('mouseleave', () => {
                item.classList.remove('hover');
            });
        });
    }

    setupKeyboardNavigation() {
        // Handle arrow key navigation for desktop menu
        document.addEventListener('keydown', (e) => {
            if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') &&
                document.activeElement.classList.contains('nav-link')) {
                this.handleArrowNavigation(e);
            }
        });
    }

    handleArrowNavigation(e) {
        const currentLink = document.activeElement;
        if (!currentLink.classList.contains('nav-link')) return;

        e.preventDefault();

        const currentIndex = Array.from(this.navLinks).indexOf(currentLink);
        let nextIndex;

        if (e.key === 'ArrowRight') {
            nextIndex = (currentIndex + 1) % this.navLinks.length;
        } else if (e.key === 'ArrowLeft') {
            nextIndex = (currentIndex - 1 + this.navLinks.length) % this.navLinks.length;
        }

        this.navLinks[nextIndex].focus();
    }

    setupActiveStates() {
        // Remove all active states first
        this.navLinks.forEach(link => {
            link.classList.remove('active');
        });

        const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Get current path and set active state
        const currentPath = window.location.pathname;

        // Check each link and set active if matches current path
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
            }
        });

        mobileNavLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
            }
        });

        // Fallback for home page
        if (currentPath === '/' || currentPath === '/home/') {
            const homeLinks = document.querySelectorAll('[href*="/home/"], [href*="/"]');
            homeLinks.forEach(link => {
                if (link.getAttribute('href') === '/' || link.getAttribute('href').includes('/home/')) {
                    link.classList.add('active');
                }
            });
        }
    }

    handleScroll() {
        let ticking = false;

        const updateNavigation = () => {
            const scrollY = window.pageYOffset;

            // Add scrolled class for styling
            if (scrollY > 10) {
                this.navbar.classList.add('scrolled');
            } else {
                this.navbar.classList.remove('scrolled');
            }

            // Определяем направление скролла
            if (scrollY > this.lastScrollY) {
                this.scrollDirection = 'down';
            } else {
                this.scrollDirection = 'up';
            }

            // Прячем навигацию при скролле вниз (только на десктопе)
            if (!this.isMobile) {
                if (this.scrollDirection === 'down' && scrollY > this.scrollThreshold) {
                    this.navbar.classList.add('hidden');
                } else {
                    this.navbar.classList.remove('hidden');
                }
            }

            // Показываем навигацию при скролле вверх или если мы вверху страницы
            if (this.scrollDirection === 'up' || scrollY <= this.scrollThreshold) {
                this.navbar.classList.remove('hidden');
            }

            this.lastScrollY = scrollY;
            ticking = false;
        };

        const onScroll = () => {
            if (!ticking) {
                requestAnimationFrame(updateNavigation);
                ticking = true;
            }
        };

        window.addEventListener('scroll', onScroll, { passive: true });
    }

    setupScrollIndicators() {
        if (!this.navMenu) return;

        // Add scroll indicators if content overflows
        const checkOverflow = () => {
            if (this.navMenu.scrollWidth > this.navMenu.clientWidth) {
                this.navMenu.parentElement.classList.add('can-scroll');
            } else {
                this.navMenu.parentElement.classList.remove('can-scroll');
            }
        };

        checkOverflow();
        window.addEventListener('resize', checkOverflow);

        // Handle scroll events for indicators
        this.navMenu.addEventListener('scroll', () => {
            this.updateScrollIndicators();
        });
    }

    updateScrollIndicators() {
        if (!this.navMenu) return;

        const scrollLeft = this.navMenu.scrollLeft;
        const scrollWidth = this.navMenu.scrollWidth;
        const clientWidth = this.navMenu.clientWidth;

        // Show/hide left indicator
        if (scrollLeft > 0) {
            this.navMenu.parentElement.classList.add('scrolled-left');
        } else {
            this.navMenu.parentElement.classList.remove('scrolled-left');
        }

        // Show/hide right indicator
        if (scrollLeft < scrollWidth - clientWidth - 1) {
            this.navMenu.parentElement.classList.add('scrolled-right');
        } else {
            this.navMenu.parentElement.classList.remove('scrolled-right');
        }
    }

    handleResize() {
        const handleResize = () => {
            this.isMobile = window.innerWidth <= 768;

            // Reset scroll behavior when switching to mobile
            if (this.isMobile) {
                this.navbar.classList.remove('hidden');
            }

            // Update scroll indicators
            this.setupScrollIndicators();
        };

        window.addEventListener('resize', handleResize);
    }

    // Public method to update active state
    setActiveItem(itemId) {
        this.navLinks.forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        });

        const mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
        mobileNavLinks.forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
        });

        const activeLink = document.querySelector(`.nav-link[href="${itemId}"]`);
        const mobileActiveLink = document.querySelector(`.mobile-nav-link[href="${itemId}"]`);

        if (activeLink) {
            activeLink.classList.add('active');
            activeLink.setAttribute('aria-current', 'page');
        }

        if (mobileActiveLink) {
            mobileActiveLink.classList.add('active');
            mobileActiveLink.setAttribute('aria-current', 'page');
        }
    }
}

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    window.Navigation = new Navigation();
});