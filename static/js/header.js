// ===== HEADER FUNCTIONALITY =====

class Header {
    constructor() {
        this.header = document.querySelector('.header');
        this.mobileMenuToggle = document.querySelector('.nav-mobile-toggle');
        this.mobileNavMenu = document.querySelector('.mobile-nav-menu');
        this.mobileNavClose = document.querySelector('.mobile-nav-close');
        this.mobileNavLinks = document.querySelectorAll('.mobile-nav-link');
        this.userMenu = document.querySelector('.user-menu');
        this.dropdownMenu = document.querySelector('.dropdown-menu');
        this.searchContainer = document.querySelector('.search-container');
        this.searchInput = document.querySelector('.search-input');
        this.searchForm = document.querySelector('.search-form');
        this.searchMobileToggle = document.querySelector('.search-mobile-toggle');

        this.isMobileMenuOpen = false;
        this.isUserMenuOpen = false;
        this.isSearchActive = false;
        this.scrollDirection = 'up';
        this.lastScrollY = window.scrollY;
        this.scrollThreshold = 100;

        this.init();
    }

    init() {
        this.bindEvents();
        this.handleScroll();
        this.handleResize();

        console.log('Header initialized 🎯');
    }

    bindEvents() {
        // Mobile menu toggle
        if (this.mobileMenuToggle) {
            this.mobileMenuToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMobileMenu();
            });
        }

        // Mobile menu close button
        if (this.mobileNavClose) {
            this.mobileNavClose.addEventListener('click', () => this.closeMobileMenu());
        }

        // Close mobile menu on link click
        this.mobileNavLinks.forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        // User menu interactions
        if (this.userMenu) {
            this.setupUserMenu();
        }

        // Search functionality
        this.setupSearch();

        // Mobile search toggle
        if (this.searchMobileToggle) {
            this.searchMobileToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleMobileSearch();
            });
        }

        // Close menus on outside click
        document.addEventListener('click', (e) => this.handleClickOutside(e));

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeAllMenus();
        });

        // Prevent search form click from closing
        if (this.searchForm) {
            this.searchForm.addEventListener('click', (e) => e.stopPropagation());
        }
    }

    toggleMobileMenu() {
        this.isMobileMenuOpen = !this.isMobileMenuOpen;

        if (this.isMobileMenuOpen) {
            this.openMobileMenu();
        } else {
            this.closeMobileMenu();
        }
    }

    openMobileMenu() {
        this.mobileNavMenu.classList.add('active');
        this.mobileMenuToggle.classList.add('active');
        this.mobileMenuToggle.setAttribute('aria-expanded', 'true');
        this.mobileNavMenu.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Close other menus
        this.closeUserMenu();
        this.closeMobileSearch();
    }

    closeMobileMenu() {
        this.isMobileMenuOpen = false;
        this.mobileNavMenu.classList.remove('active');
        this.mobileMenuToggle.classList.remove('active');
        this.mobileMenuToggle.setAttribute('aria-expanded', 'false');
        this.mobileNavMenu.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    setupUserMenu() {
        const userTrigger = this.userMenu.querySelector('.user-trigger');

        if (userTrigger) {
            userTrigger.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserMenu();
            });
        }

        // Close dropdown when clicking on items
        if (this.dropdownMenu) {
            this.dropdownMenu.addEventListener('click', (e) => {
                if (e.target.closest('.dropdown-item')) {
                    this.closeUserMenu();
                }
            });
        }
    }

    toggleUserMenu() {
        this.isUserMenuOpen = !this.isUserMenuOpen;

        if (this.isUserMenuOpen) {
            this.dropdownMenu.classList.add('show');
            this.userMenu.querySelector('.user-trigger').setAttribute('aria-expanded', 'true');

            // Close other menus
            this.closeMobileMenu();
            this.closeMobileSearch();
        } else {
            this.closeUserMenu();
        }
    }

    closeUserMenu() {
        this.isUserMenuOpen = false;
        if (this.dropdownMenu) {
            this.dropdownMenu.classList.remove('show');
        }
        const userTrigger = this.userMenu?.querySelector('.user-trigger');
        if (userTrigger) {
            userTrigger.setAttribute('aria-expanded', 'false');
        }
    }

    setupSearch() {
        // Handle search form submission
        if (this.searchForm) {
            this.searchForm.addEventListener('submit', (e) => {
                const input = this.searchForm.querySelector('input');
                if (!input.value.trim()) {
                    e.preventDefault();
                    input.focus();
                    this.showSearchError('Введите поисковый запрос');
                }
            });
        }

        // Auto-focus search input when opened on mobile
        if (this.searchInput) {
            this.searchInput.addEventListener('focus', () => {
                if (window.innerWidth <= 768) {
                    this.openMobileSearch();
                }
            });
        }
    }

    toggleMobileSearch() {
        this.isSearchActive = !this.isSearchActive;

        if (this.isSearchActive) {
            this.openMobileSearch();
        } else {
            this.closeMobileSearch();
        }
    }

    openMobileSearch() {
        if (window.innerWidth <= 768 && this.searchContainer) {
            this.isSearchActive = true;
            this.searchContainer.classList.add('active');

            // Focus search input
            setTimeout(() => {
                if (this.searchInput) {
                    this.searchInput.focus();
                }
            }, 100);

            // Close other menus
            this.closeMobileMenu();
            this.closeUserMenu();
        }
    }

    closeMobileSearch() {
        this.isSearchActive = false;
        if (this.searchContainer) {
            this.searchContainer.classList.remove('active');
        }
    }

    showSearchError(message) {
        // Можно подключить к вашей системе уведомлений
        console.warn(message);

        // Визуальная обратная связь
        if (this.searchInput) {
            this.searchInput.style.borderColor = '#ff6b6b';
            this.searchInput.style.boxShadow = '0 0 0 3px rgba(255, 107, 107, 0.1)';

            setTimeout(() => {
                this.searchInput.style.borderColor = '';
                this.searchInput.style.boxShadow = '';
            }, 2000);
        }
    }

    handleClickOutside(e) {
        // Закрыть мобильное меню при клике вне
        if (this.isMobileMenuOpen &&
            !this.mobileNavMenu.contains(e.target) &&
            !this.mobileMenuToggle.contains(e.target)) {
            this.closeMobileMenu();
        }

        // Закрыть пользовательское меню при клике вне
        if (this.isUserMenuOpen && this.userMenu && !this.userMenu.contains(e.target)) {
            this.closeUserMenu();
        }

        // Закрыть мобильный поиск при клике вне
        if (this.isSearchActive &&
            !this.searchContainer.contains(e.target) &&
            !this.searchMobileToggle.contains(e.target)) {
            this.closeMobileSearch();
        }
    }

    closeAllMenus() {
        this.closeMobileMenu();
        this.closeUserMenu();
        this.closeMobileSearch();
    }

    handleScroll() {
        let ticking = false;

        const updateHeader = () => {
            const scrollY = window.scrollY;

            // Добавить/удалить класс scrolled
            if (scrollY > 10) {
                this.header.classList.add('scrolled');
            } else {
                this.header.classList.remove('scrolled');
            }

            // Определяем направление скролла
            if (scrollY > this.lastScrollY) {
                this.scrollDirection = 'down';
            } else {
                this.scrollDirection = 'up';
            }

            // Скрываем хедер при скролле вниз
            if (this.scrollDirection === 'down' && scrollY > this.scrollThreshold) {
                this.header.style.transform = 'translateY(-100%)';
            } else {
                this.header.style.transform = 'translateY(0)';
            }

            // Показываем хедер при скролле вверх или если мы вверху страницы
            if (this.scrollDirection === 'up' || scrollY <= this.scrollThreshold) {
                this.header.style.transform = 'translateY(0)';
            }

            this.lastScrollY = scrollY;
            ticking = false;
        };

        const onScroll = () => {
            if (!ticking) {
                requestAnimationFrame(updateHeader);
                ticking = true;
            }
        };

        window.addEventListener('scroll', onScroll, { passive: true });
    }

    handleResize() {
        const handleResize = () => {
            // Закрыть все меню при переходе на десктоп
            if (window.innerWidth > 768) {
                this.closeAllMenus();
                this.isSearchActive = false;

                // Сбросить позицию хедера
                this.header.style.transform = 'translateY(0)';
            }
        };

        window.addEventListener('resize', handleResize);
    }
}

// Initialize header
document.addEventListener('DOMContentLoaded', () => {
    window.Header = new Header();
});