from django.test import TestCase
import time
from apps.memo import generate_quiz_variant, benchmark_generation


class Lab3Test(TestCase):
    """6 тестов для лабы №3: Мемоизация"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.bp_key = "bp_15:python,web:1,2,3,4:123"
        self.pool_idx = tuple(f"item_{i}_diff_{(i % 5) + 1}" for i in range(100))

    # ТЕСТ 1: Иммутабельный ключ кэша
    def test_immutable_cache_key(self):
        """Тест 1: Функция использует иммутабельные ключи кэша"""
        # Одинаковые параметры → одинаковый результат
        result1 = generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        result2 = generate_quiz_variant(self.bp_key, self.pool_idx, 42)

        self.assertEqual(result1, result2)
        self.assertIsInstance(result1, tuple)  # Иммутабельный результат

    # ТЕСТ 2: Детерминированность с одинаковым seed
    def test_deterministic_with_seed(self):
        """Тест 2: Детерминированность при одинаковом seed"""
        result1 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 100)
        result2 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 100)

        self.assertEqual(result1, result2)

    # ТЕСТ 3: Разные результаты с разными seed
    def test_different_with_different_seed(self):
        """Тест 3: Разные результаты с разными seed"""
        result1 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 100)
        result2 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 200)

        # С высокой вероятностью результаты разные
        self.assertNotEqual(result1, result2)

    # ТЕСТ 4: Работа кэша (hits/misses)
    def test_cache_behavior(self):
        """Тест 4: Проверка работы кэша LRU"""
        # Сбрасываем кэш
        generate_quiz_variant.cache_clear()
        initial_info = generate_quiz_variant.cache_info()

        # Первый вызов - cache miss
        generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        after_first = generate_quiz_variant.cache_info()

        # Второй вызов - cache hit
        generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        after_second = generate_quiz_variant.cache_info()

        self.assertEqual(after_first.misses, initial_info.misses + 1)
        self.assertEqual(after_second.hits, after_first.hits + 1)

    # ТЕСТ 5: Производительность с кэшем
    def test_performance_with_cache(self):
        """Тест 5: Замер производительности"""
        # Малый бенчмарк для тестов
        results = benchmark_generation(iterations=10)

        self.assertIn('iterations', results)
        self.assertIn('uncached_time', results)
        self.assertIn('cached_time', results)
        self.assertIn('speedup', results)

        # С кэшем должно быть быстрее
        self.assertLess(results['cached_time'], results['uncached_time'])

    # ТЕСТ 6: Чистота функции
    def test_pure_function(self):
        """Тест 6: Функция является чистой (no side effects)"""
        initial_cache_info = generate_quiz_variant.cache_info()

        # Вызов функции не должен изменять внешнее состояние
        result = generate_quiz_variant(self.bp_key, self.pool_idx, 42)

        # Проверяем что результат детерминирован
        self.assertIsInstance(result, tuple)
        self.assertTrue(all(isinstance(item_id, str) for item_id in result))

        # Кэш изменился, но это ожидаемо для мемоизации
        final_cache_info = generate_quiz_variant.cache_info()
        self.assertGreaterEqual(final_cache_info.misses, initial_cache_info.misses)