from django.test import TestCase
import time
from apps.memo import generate_quiz_variant, benchmark_generation


class Lab3Test(TestCase):
    """5 тестов для лабы №3: Мемоизация и рекурсия"""

    def setUp(self):
        self.bp_key = "bp_15:python,web:1,2,3,4:123"
        self.pool_idx = tuple(f"item_{i}diff{(i % 5) + 1}" for i in range(100))

    # ТЕСТ 1: Иммутабельный ключ кэша
    def test_immutable_cache_key(self):
        """Тест 1: Функция использует иммутабельные ключи кэша"""
        result1 = generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        result2 = generate_quiz_variant(self.bp_key, self.pool_idx, 42)

        self.assertEqual(result1, result2)
        self.assertIsInstance(result1, tuple)

    # ТЕСТ 2: Детерминированность с одинаковым seed
    def test_deterministic_with_seed(self):
        """Тест 2: Детерминированность при одинаковом seed"""
        result1 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 100)
        result2 = generate_quiz_variant("bp_10:python:1,2:100", self.pool_idx, 100)

        self.assertEqual(result1, result2)

    # ТЕСТ 3: Работа кэша (hits/misses)
    def test_cache_behavior(self):
        """Тест 3: Проверка работы кэша LRU"""
        generate_quiz_variant.cache_clear()

        # Первый вызов - cache miss
        generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        after_first = generate_quiz_variant.cache_info()

        # Второй вызов - cache hit
        generate_quiz_variant(self.bp_key, self.pool_idx, 42)
        after_second = generate_quiz_variant.cache_info()

        self.assertEqual(after_first.misses, 1)
        self.assertEqual(after_second.hits, 1)

    # ТЕСТ 4: Производительность с кэшем
    def test_performance_with_cache(self):
        """Тест 4: Замер производительности"""
        results = benchmark_generation(iterations=10)

        self.assertIn('iterations', results)
        self.assertIn('uncached_time', results)
        self.assertIn('cached_time', results)
        self.assertIn('speedup', results)

    # ТЕСТ 5: Рекурсивная балансировка
    def test_recursive_balancing(self):
        """Тест 5: Продвинутая рекурсивная балансировка"""
        bp_key = "bp_10:python:1,2,3:42"
        pool_idx = tuple(f"item_{i}diff{(i % 3) + 1}" for i in range(50))

        variant = generate_quiz_variant(bp_key, pool_idx, 42)

        # Проверяем что рекурсивная балансировка работает
        self.assertIsInstance(variant, tuple)
        self.assertEqual(len(variant), 10)

        # Проверяем что задания содержат указанные сложности
        difficulties_used = set()
        for item in variant:
            for diff in [1, 2, 3]:
                if f"diff{diff}" in item:
                    difficulties_used.add(diff)

        # Должны быть использованы все указанные сложности
        self.assertTrue(all(diff in difficulties_used for diff in [1, 2, 3]))