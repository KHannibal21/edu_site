// ===== ANALYTICS PAGE FUNCTIONALITY =====

class AnalyticsPage {
    constructor() {
        this.counterElements = document.querySelectorAll('.stat-number[data-count]');
        this.progressBars = document.querySelectorAll('.progress-fill');
        this.chartBars = document.querySelectorAll('.chart-bar');
        this.ringSegments = document.querySelectorAll('.ring-segment');
        this.cards = document.querySelectorAll('.analytics-card');

        this.init();
    }

    init() {
        this.animateElements();
        this.setupInteractions();
        this.setupAnimations();

        console.log('Analytics page initialized 📊');
    }

    animateElements() {
        // Анимация счетчиков
        this.counterElements.forEach(counter => {
            this.animateCounter(counter);
        });

        // Анимация прогресс-баров
        setTimeout(() => {
            this.progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {
                    bar.style.width = width;
                }, 300);
            });
        }, 500);

        // Анимация столбцов графика
        setTimeout(() => {
            this.chartBars.forEach(bar => {
                const height = bar.style.height;
                bar.style.height = '0%';
                setTimeout(() => {
                    bar.style.height = height;
                }, 600);
            });
        }, 800);

        // Анимация кольцевых диаграмм
        setTimeout(() => {
            this.ringSegments.forEach(segment => {
                const originalDasharray = segment.getAttribute('stroke-dasharray');
                const originalDashoffset = segment.getAttribute('stroke-dashoffset');

                segment.setAttribute('stroke-dasharray', '0 339.292');
                setTimeout(() => {
                    segment.setAttribute('stroke-dasharray', originalDasharray);
                    segment.setAttribute('stroke-dashoffset', originalDashoffset);
                }, 400);
            });
        }, 1000);
    }

    animateCounter(counter) {
        const target = parseInt(counter.getAttribute('data-count'));
        const suffix = counter.textContent.includes('₽') ? '₽' :
                      counter.textContent.includes('%') ? '%' : '';
        const duration = 2000;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                counter.textContent = this.formatNumber(target) + suffix;
                clearInterval(timer);
            } else {
                counter.textContent = this.formatNumber(Math.floor(current)) + suffix;
            }
        }, stepTime);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K';
        }
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    }

    setupInteractions() {
        // Кнопки переключения фильтров
        const filterButtons = document.querySelectorAll('.card-actions .btn');
        filterButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();

                // Убираем активный класс со всех кнопок
                filterButtons.forEach(btn => {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline');
                });

                // Добавляем активный класс текущей кнопке
                button.classList.remove('btn-outline');
                button.classList.add('btn-primary');

                // Здесь можно добавить логику обновления данных
                console.log('Фильтр изменен:', button.textContent);
            });
        });

        // Имитация обновления данных каждые 30 секунд
        setInterval(() => {
            this.simulateLiveUpdate();
        }, 30000);
    }

    setupAnimations() {
        // Анимация появления карточек
        this.cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';

            setTimeout(() => {
                card.style.transition = 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Параллакс эффект для карточек
        document.addEventListener('mousemove', (e) => {
            if (window.innerWidth > 768) {
                this.cards.forEach((card, index) => {
                    const speed = 0.5 + (index * 0.1);
                    const x = (window.innerWidth - e.pageX * speed) / 100;
                    const y = (window.innerHeight - e.pageY * speed) / 100;

                    card.style.transform = `translate(${x}px, ${y}px)`;
                });
            }
        });
    }

    simulateLiveUpdate() {
        // Имитация обновления данных
        const counters = document.querySelectorAll('.stat-number[data-count]');
        counters.forEach(counter => {
            const currentValue = parseInt(counter.textContent.replace(/[^0-9]/g, ''));
            const increment = Math.floor(Math.random() * 10) + 1;
            const newValue = currentValue + increment;

            // Обновляем data-count атрибут
            counter.setAttribute('data-count', newValue);

            // Быстрая анимация обновления
            this.quickAnimateCounter(counter, currentValue, newValue);
        });

        console.log('Данные обновлены 🔄');
    }

    quickAnimateCounter(counter, start, end) {
        const suffix = counter.textContent.includes('₽') ? '₽' :
                      counter.textContent.includes('%') ? '%' : '';
        const duration = 800;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = (end - start) / steps;
        let current = start;

        const timer = setInterval(() => {
            current += increment;
            if (current >= end) {
                counter.textContent = this.formatNumber(end) + suffix;
                clearInterval(timer);
            } else {
                counter.textContent = this.formatNumber(Math.floor(current)) + suffix;
            }
        }, stepTime);
    }

    // Методы для обновления данных (можно расширить)
    updateChartData(chartId, newData) {
        console.log(`Обновление графика ${chartId}:`, newData);
        // Здесь можно добавить логику обновления конкретного графика
    }

    refreshAllData() {
        console.log('Обновление всех данных...');
        this.animateElements();
    }
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    window.AnalyticsPage = new AnalyticsPage();

    // Добавляем глобальную функцию для обновления данных
    window.refreshAnalytics = () => {
        window.AnalyticsPage.refreshAllData();
    };

    // Добавляем обработчик для кнопки обновления (если она есть)
    const refreshButton = document.querySelector('.refresh-analytics');
    if (refreshButton) {
        refreshButton.addEventListener('click', () => {
            window.AnalyticsPage.refreshAllData();

            // Визуальная обратная связь
            refreshButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            setTimeout(() => {
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i> Обновить';
            }, 1000);
        });
    }
});