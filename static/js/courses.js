// Мок данные курсов (расширенный набор)
const mockCourses = [
    {
        id: 1,
        title: "Python с нуля до PRO",
        description: "Освойте один из самых популярных языков программирования с практическими проектами. Идеально для начинающих.",
        category: "programming",
        level: "Начальный",
        duration: "48 часов",
        lessons: 32,
        students: 2450,
        rating: 4.9,
        reviews: 2100,
        price: 14900,
        oldPrice: 19900,
        icon: "fab fa-python",
        badge: "bestseller",
        color: "#667eea"
    },
    {
        id: 2,
        title: "Веб-разработка 2025",
        description: "Создавайте современные веб-приложения с React, Node.js и современными фреймворками.",
        category: "programming",
        level: "Средний",
        duration: "72 часа",
        lessons: 48,
        students: 1890,
        rating: 4.8,
        reviews: 1780,
        price: 19900,
        oldPrice: 26900,
        icon: "fas fa-laptop-code",
        badge: "hot",
        color: "#764ba2"
    },
    {
        id: 3,
        title: "UI/UX дизайн PRO",
        description: "Освойте создание удобных и красивых интерфейсов. Figma, принципы UX и современные тренды.",
        category: "design",
        level: "Средний",
        duration: "56 часов",
        lessons: 42,
        students: 1560,
        rating: 4.7,
        reviews: 1420,
        price: 17900,
        oldPrice: 23900,
        icon: "fas fa-paint-brush",
        badge: "new",
        color: "#f093fb"
    },
    {
        id: 4,
        title: "Digital Marketing",
        description: "Освойте современные инструменты интернет-маркетинга: SMM, SEO, контекстная реклама.",
        category: "marketing",
        level: "Начальный",
        duration: "40 часов",
        lessons: 30,
        students: 2100,
        rating: 4.6,
        reviews: 1890,
        price: 15900,
        oldPrice: 21900,
        icon: "fas fa-chart-line",
        badge: "bestseller",
        color: "#f5576c"
    },
    {
        id: 5,
        title: "Data Science",
        description: "Анализ данных и машинное обучение. Python, Pandas, Scikit-learn и глубокое обучение.",
        category: "data",
        level: "Продвинутый",
        duration: "96 часов",
        lessons: 64,
        students: 1250,
        rating: 4.9,
        reviews: 1150,
        price: 24900,
        oldPrice: 32900,
        icon: "fas fa-database",
        badge: "new",
        color: "#1e3c72"
    },
    {
        id: 6,
        title: "Мобильная разработка",
        description: "Создание приложений для iOS и Android на Swift и Kotlin. React Native для кроссплатформы.",
        category: "mobile",
        level: "Средний",
        duration: "64 часа",
        lessons: 48,
        students: 1780,
        rating: 4.8,
        reviews: 1620,
        price: 21900,
        oldPrice: 28900,
        icon: "fas fa-mobile-alt",
        badge: "hot",
        color: "#2a5298"
    },
    {
        id: 7,
        title: "Бизнес-аналитика",
        description: "Научитесь принимать решения на основе данных. Excel, SQL, Power BI и визуализация.",
        category: "business",
        level: "Средний",
        duration: "52 часов",
        lessons: 36,
        students: 1450,
        rating: 4.7,
        reviews: 1320,
        price: 18900,
        oldPrice: 24900,
        icon: "fas fa-briefcase",
        badge: null,
        color: "#4f46e5"
    },
    {
        id: 8,
        title: "Графический дизайн",
        description: "Основы работы в Adobe Photoshop, Illustrator и создание профессиональной графики.",
        category: "design",
        level: "Начальный",
        duration: "44 часа",
        lessons: 32,
        students: 1980,
        rating: 4.6,
        reviews: 1780,
        price: 16900,
        oldPrice: 22900,
        icon: "fas fa-palette",
        badge: "free",
        color: "#7c3aed"
    }
];

// Конфигурация
const config = {
    coursesPerPage: 8,
    currentPage: 1,
    currentFilter: 'all',
    currentLevel: 'all',
    currentSort: 'popular'
};

// DOM элементы
let coursesGrid;
let searchInput;
let clearSearchBtn;
let filterCategoryBtns;
let filterOptionBtns;
let noCoursesMessage;
let resetFiltersBtn;
let prevPageBtn;
let nextPageBtn;
let coursesCountElement;

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    initElements();
    initEventListeners();
    initAnimations();

    // Показать скелетоны
    showSkeletons();

    // Загрузить курсы с задержкой (имитация загрузки)
    setTimeout(() => {
        renderCourses(getFilteredCourses());
        hideSkeletons();
        updatePagination();
    }, 800);
});

// Инициализация элементов
function initElements() {
    coursesGrid = document.getElementById('coursesGrid');
    searchInput = document.getElementById('searchCourses');
    clearSearchBtn = document.getElementById('clearSearch');
    filterCategoryBtns = document.querySelectorAll('.filter-category-btn');
    filterOptionBtns = document.querySelectorAll('.filter-option-btn');
    noCoursesMessage = document.getElementById('noCoursesMessage');
    resetFiltersBtn = document.getElementById('resetFilters');
    prevPageBtn = document.getElementById('prevPage');
    nextPageBtn = document.getElementById('nextPage');
    coursesCountElement = document.getElementById('coursesCount');
}

// Инициализация обработчиков событий
function initEventListeners() {
    // Поиск
    searchInput.addEventListener('input', handleSearch);
    clearSearchBtn.addEventListener('click', clearSearch);

    // Фильтрация по категориям
    filterCategoryBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterCategoryBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            config.currentFilter = btn.dataset.filter;
            updateCourses();
        });
    });

    // Фильтрация по уровню
    document.querySelectorAll('[data-level]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-level]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            config.currentLevel = btn.dataset.level;
            updateCourses();
        });
    });

    // Сортировка
    document.querySelectorAll('[data-sort]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-sort]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            config.currentSort = btn.dataset.sort;
            updateCourses();
        });
    });

    // Сброс фильтров
    resetFiltersBtn.addEventListener('click', resetFilters);

    // Пагинация
    prevPageBtn.addEventListener('click', goToPrevPage);
    nextPageBtn.addEventListener('click', goToNextPage);

    // Нажатие Enter в поиске
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') updateCourses();
    });
}

// Инициализация анимаций
function initAnimations() {
    // Анимация появления элементов
    const animateElements = document.querySelectorAll('[data-animate]');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, { threshold: 0.1 });

    animateElements.forEach(el => observer.observe(el));

    // Анимация прогресс-баров
    animateProgressBars();
}

// Обработка поиска
function handleSearch() {
    if (searchInput.value.trim()) {
        clearSearchBtn.style.display = 'block';
    } else {
        clearSearchBtn.style.display = 'none';
        updateCourses();
    }
}

// Очистка поиска
function clearSearch() {
    searchInput.value = '';
    clearSearchBtn.style.display = 'none';
    updateCourses();
}

// Обновление курсов
function updateCourses() {
    showSkeletons();
    setTimeout(() => {
        const filteredCourses = getFilteredCourses();
        renderCourses(filteredCourses);
        hideSkeletons();
        updatePagination();
        updateCoursesCount(filteredCourses.length);
    }, 300);
}

// Получение отфильтрованных курсов
function getFilteredCourses() {
    let filtered = [...mockCourses];

    // Фильтрация по категории
    if (config.currentFilter !== 'all') {
        filtered = filtered.filter(course => course.category === config.currentFilter);
    }

    // Фильтрация по уровню
    if (config.currentLevel !== 'all') {
        const levelMap = {
            'beginner': 'Начальный',
            'intermediate': 'Средний',
            'advanced': 'Продвинутый'
        };
        filtered = filtered.filter(course => course.level === levelMap[config.currentLevel]);
    }

    // Поиск
    const searchTerm = searchInput.value.toLowerCase().trim();
    if (searchTerm) {
        filtered = filtered.filter(course =>
            course.title.toLowerCase().includes(searchTerm) ||
            course.description.toLowerCase().includes(searchTerm)
        );
    }

    // Сортировка
    filtered.sort((a, b) => {
        switch(config.currentSort) {
            case 'new':
                return b.id - a.id;
            case 'rating':
                return b.rating - a.rating;
            case 'price':
                return a.price - b.price;
            default: // popular
                return b.students - a.students;
        }
    });

    return filtered;
}

// Показать скелетоны
function showSkeletons() {
    coursesGrid.innerHTML = '';

    for (let i = 0; i < config.coursesPerPage; i++) {
        const skeletonHTML = `
            <div class="course-card skeleton">
                <div class="course-image skeleton" style="height: 200px"></div>
                <div class="course-content">
                    <div class="skeleton" style="height: 20px; width: 30%; margin-bottom: 10px"></div>
                    <div class="skeleton" style="height: 25px; width: 80%; margin-bottom: 15px"></div>
                    <div class="skeleton" style="height: 60px; margin-bottom: 20px"></div>
                    <div class="skeleton" style="height: 40px"></div>
                </div>
            </div>
        `;
        coursesGrid.innerHTML += skeletonHTML;
    }
}

// Скрыть скелетоны
function hideSkeletons() {
    // Автоматически скрываются при рендере
}

// Рендер курсов
function renderCourses(courses) {
    if (courses.length === 0) {
        coursesGrid.style.display = 'none';
        noCoursesMessage.style.display = 'block';
        return;
    }

    coursesGrid.style.display = 'grid';
    noCoursesMessage.style.display = 'none';

    // Рассчитать, какие курсы показывать для текущей страницы
    const startIndex = (config.currentPage - 1) * config.coursesPerPage;
    const endIndex = startIndex + config.coursesPerPage;
    const coursesToShow = courses.slice(startIndex, endIndex);

    coursesGrid.innerHTML = '';

    coursesToShow.forEach((course, index) => {
        const courseCard = createCourseCard(course, index);
        coursesGrid.appendChild(courseCard);
    });

    // Анимация появления
    animateCourses();
}

// Создание карточки курса
function createCourseCard(course, index) {
    const card = document.createElement('div');
    card.className = 'course-card';
    card.style.animationDelay = `${index * 0.1}s`;

    // Бейдж
    let badgeHTML = '';
    if (course.badge) {
        badgeHTML = `<div class="course-badge course-${course.badge}">${getBadgeText(course.badge)}</div>`;
    }

    // Звезды рейтинга
    const starsHTML = generateStars(course.rating);

    card.innerHTML = `
        ${badgeHTML}
        <div class="course-image" style="background: linear-gradient(135deg, ${course.color} 0%, ${darkenColor(course.color, 20)} 100%)">
            <div class="course-image-placeholder">
                <i class="${course.icon}"></i>
            </div>
            <span class="course-level">${course.level}</span>
        </div>
        <div class="course-content">
            <div class="course-category">
                <i class="${getCategoryIcon(course.category)}"></i>
                ${getCategoryName(course.category)}
            </div>
            <h3 class="course-title">${course.title}</h3>
            <p class="course-description">${course.description}</p>

            <div class="course-meta">
                <span class="course-duration">
                    <i class="fas fa-clock"></i>
                    ${course.duration}
                </span>
                <span class="course-lessons">
                    <i class="fas fa-book"></i>
                    ${course.lessons} уроков
                </span>
                <span class="course-students">
                    <i class="fas fa-users"></i>
                    ${formatNumber(course.students)}
                </span>
            </div>

            <div class="course-rating">
                <div class="course-stars">
                    ${starsHTML}
                </div>
                <span>${course.rating} (${formatNumber(course.reviews)})</span>
            </div>

            <div class="course-footer">
                <div class="course-price">
                    <span class="course-price-current">${formatPrice(course.price)} тг</span>
                    <span class="course-price-old">${formatPrice(course.oldPrice)} тг</span>
                </div>
                <button class="btn-course" onclick="viewCourse(${course.id})">
                    Подробнее
                    <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `;

    return card;
}

// Анимация появления курсов
function animateCourses() {
    const cards = document.querySelectorAll('.course-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';

        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Анимация прогресс-баров
function animateProgressBars() {
    const progressBars = document.querySelectorAll('.home-progress-fill');
    progressBars.forEach(bar => {
        const width = bar.getAttribute('data-width') || '85';
        setTimeout(() => {
            bar.style.width = `${width}%`;
        }, 500);
    });
}

// Обновление пагинации
function updatePagination() {
    const filteredCourses = getFilteredCourses();
    const totalPages = Math.ceil(filteredCourses.length / config.coursesPerPage);

    prevPageBtn.disabled = config.currentPage === 1;
    nextPageBtn.disabled = config.currentPage === totalPages || totalPages === 0;
}

// Обновление счетчика курсов
function updateCoursesCount(count) {
    coursesCountElement.textContent = count;
}

// Сброс всех фильтров
function resetFilters() {
    // Сброс категории
    filterCategoryBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === 'all') {
            btn.classList.add('active');
        }
    });

    // Сброс уровня
    document.querySelectorAll('[data-level]').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.level === 'all') {
            btn.classList.add('active');
        }
    });

    // Сброс сортировки
    document.querySelectorAll('[data-sort]').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.sort === 'popular') {
            btn.classList.add('active');
        }
    });

    // Сброс поиска
    searchInput.value = '';
    clearSearchBtn.style.display = 'none';

    // Сброс конфигурации
    config.currentFilter = 'all';
    config.currentLevel = 'all';
    config.currentSort = 'popular';
    config.currentPage = 1;

    updateCourses();
}

// Переход на предыдущую страницу
function goToPrevPage() {
    if (config.currentPage > 1) {
        config.currentPage--;
        updateCourses();
    }
}

// Переход на следующую страницу
function goToNextPage() {
    const filteredCourses = getFilteredCourses();
    const totalPages = Math.ceil(filteredCourses.length / config.coursesPerPage);

    if (config.currentPage < totalPages) {
        config.currentPage++;
        updateCourses();
    }
}

// Просмотр курса (заглушка)
function viewCourse(courseId) {
    console.log(`Просмотр курса ${courseId}`);
    // В реальном приложении здесь будет редирект
    alert(`В реальном приложении здесь будет переход к курсу ${courseId}`);
}

// Вспомогательные функции
function getBadgeText(badge) {
    const badges = {
        'bestseller': 'Бестселлер',
        'hot': 'Горячий',
        'new': 'Новый',
        'free': 'Бесплатно'
    };
    return badges[badge] || badge;
}

function getCategoryName(category) {
    const categories = {
        'programming': 'Программирование',
        'design': 'Дизайн',
        'marketing': 'Маркетинг',
        'business': 'Бизнес',
        'data': 'Data Science',
        'mobile': 'Мобильная разработка'
    };
    return categories[category] || category;
}

function getCategoryIcon(category) {
    const icons = {
        'programming': 'fas fa-code',
        'design': 'fas fa-paint-brush',
        'marketing': 'fas fa-chart-line',
        'business': 'fas fa-briefcase',
        'data': 'fas fa-database',
        'mobile': 'fas fa-mobile-alt'
    };
    return icons[category] || 'fas fa-graduation-cap';
}

function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1).replace('.0', '') + 'k';
    }
    return num.toString();
}

function generateStars(rating) {
    let stars = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }

    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }

    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }

    return stars;
}

function darkenColor(color, percent) {
    const num = parseInt(color.replace("#", ""), 16);
    const amt = Math.round(2.55 * percent);
    const R = (num >> 16) - amt;
    const G = (num >> 8 & 0x00FF) - amt;
    const B = (num & 0x0000FF) - amt;

    return "#" + (
        0x1000000 +
        (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
        (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
        (B < 255 ? B < 1 ? 0 : B : 255)
    ).toString(16).slice(1);
}

// Экспорт для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { mockCourses, getFilteredCourses };
}