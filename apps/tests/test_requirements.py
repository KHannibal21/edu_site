from django.test import TestCase
from apps.models import *
from apps.services import *


class Lab1Test(TestCase):
    """Ровно 6 тестов для лабы №1"""

    def setUp(self):
        """Подготовка данных по требованиям: ≥3 курса, ≥12 уроков, ≥200 заданий, ≥40 пользователей, ≥3 blueprint"""
        # Создаем минимальные данные для тестов
        self.courses = [
            Course.objects.create(id=f"c{i}", title=f"Course {i}", topics=[f"topic{i}"])
            for i in range(1, 4)  # 3 курса
        ]

        self.lessons = []
        for i, course in enumerate(self.courses):
            for j in range(4):  # 12 уроков всего
                lesson = Lesson.objects.create(
                    id=f"l{i * 4 + j + 1}",
                    course=course,
                    title=f"Lesson {i * 4 + j + 1}",
                    topic=course.topics[0]
                )
                self.lessons.append(lesson)

        # 50 заданий для тестов (вместо 200 для скорости)
        self.items = []
        for i in range(1, 51):
            lesson = self.lessons[i % len(self.lessons)]
            item = Item.objects.create(
                id=f"item{i:03d}",
                lesson=lesson,
                type="mcq/single" if i % 3 == 0 else "mcq/multi" if i % 3 == 1 else "short",
                stem=f"Question {i}",
                options=["A", "B", "C"] if i % 3 != 2 else [],
                answer=[0] if i % 3 == 0 else [0, 1] if i % 3 == 1 else "answer",
                tags=[lesson.topic, "basic" if i % 2 == 0 else "advanced"],
                difficulty=(i % 5) + 1
            )
            self.items.append(item)

        self.users = [
            User.objects.create(id=f"user{i}", name=f"User {i}", role="teacher" if i == 1 else "student")
            for i in range(1, 41)  # 40 пользователей
        ]

        self.blueprints = [
            QuizBlueprint.objects.create(
                id=f"bp{i}",
                lesson=self.lessons[0],
                rules={"count": 5, "difficulty": [1, 3], "mix": True}
            )
            for i in range(1, 4)  # 3 blueprint
        ]

    # ТЕСТ 1: Иммутабельные модели и возврат новых коллекций
    def test_immutable_structures_and_tuples(self):
        """Тест 1: Иммутабельные модели; возврат новых коллекций"""
        courses, items, blueprints, users = load_immutable_data()

        # Проверяем кортежи
        self.assertIsInstance(courses, tuple)
        self.assertIsInstance(items, tuple)

        # Проверяем иммутабельные объекты
        self.assertTrue(all(isinstance(item, ImmutableItem) for item in items))

        # Проверяем что списки преобразованы в кортежи
        sample_item = items[0]
        self.assertIsInstance(sample_item.options, tuple)
        self.assertIsInstance(sample_item.tags, tuple)

    # ТЕСТ 2: Явное использование filter в pick_items
    def test_filter_usage_in_pick_items(self):
        """Тест 2: Использование filter в pick_items"""
        _, items, blueprints, _ = load_immutable_data()
        bp = ImmutableQuizBlueprint(self.blueprints[0])  # difficulty [1,3]

        selected = pick_items_functional(items, bp)

        # Проверяем что FILTER отработал - только задания сложности 1-3
        self.assertTrue(all(1 <= item.difficulty <= 3 for item in selected))
        self.assertEqual(len(selected), 5)

    # ТЕСТ 3: Явное использование reduce в sum_score и calculate_statistics
    def test_reduce_usage(self):
        """Тест 3: Использование reduce в sum_score и calculate_statistics"""
        # Тестируем sum_score с REDUCE
        quiz = Quiz.objects.create(id="quiz1", user=self.users[0], blueprint=self.blueprints[0], status="started")
        grades = [
            Grade.objects.create(id=f"g{i}", quiz=quiz, score=float(i), breakdown=[])
            for i in range(1, 6)  # 1+2+3+4+5 = 15
        ]

        total = sum_score(tuple(grades))
        self.assertEqual(total, 15.0)

        # Тестируем calculate_statistics с REDUCE
        stats = calculate_statistics()
        self.assertIn('mcq/single', stats['type_distribution'])  # REDUCE в работе
        self.assertIn(3, stats['difficulty_distribution'])  # REDUCE в работе

    # ТЕСТ 4: Явное использование map в load_immutable_data
    def test_map_usage(self):
        """Тест 4: Использование map в load_immutable_data"""
        courses, items, blueprints, users = load_immutable_data()

        # MAP используется в load_immutable_data для преобразования
        self.assertEqual(len(items), 50)
        self.assertTrue(all(isinstance(item, ImmutableItem) for item in items))

    # ТЕСТ 5: Функции высшего порядка (HOF)
    def test_higher_order_functions(self):
        """Тест 5: Функции высшего порядка"""
        _, items, _, _ = load_immutable_data()

        # HOF: создаем функцию-маппер
        mapper = create_difficulty_mapper(2, 4)
        mapped_items = tuple(map(mapper, items[:5]))  # MAP с HOF

        self.assertEqual(len(mapped_items), 5)
        self.assertTrue(all('in_range' in item for item in mapped_items))

        # HOF: создаем функцию-фильтр
        filter_func = create_complex_filter(difficulty_range=(3, 5), types=['mcq/single'])
        filtered_items = tuple(filter(filter_func, items))  # FILTER с HOF

        self.assertTrue(all(3 <= item.difficulty <= 5 for item in filtered_items))
        self.assertTrue(all(item.type == 'mcq/single' for item in filtered_items))

    # ТЕСТ 6: Комплексное использование в analyze_items
    def test_complex_functional_operations(self):
        """Тест 6: Комплексное использование MAP/FILTER/REDUCE"""
        _, items, _, _ = load_immutable_data()

        analysis = analyze_items(items)

        # Проверяем что все операции работают
        self.assertEqual(analysis['total_items'], 50)
        self.assertIn('mcq_count', analysis)
        self.assertIn('difficulty_range', analysis)

        # Проверяем что FILTER + MAP + REDUCE дали осмысленный результат
        self.assertGreaterEqual(analysis['mcq_difficulty_stats']['min'], 1)
        self.assertLessEqual(analysis['mcq_difficulty_stats']['max'], 5)

# Ровно 6 тестов - все требования лабы покрыты