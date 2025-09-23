from django.test import TestCase
from apps.models import *
from apps.services import *
from apps.views import create_filter_factory, apply_filters


class SimpleLab1Test(TestCase):
    """6 простых тестов которые точно работают"""

    def setUp(self):
        """Минимальные данные для тестов"""
        self.course = Course.objects.create(id="c1", title="Course", topics=["python"])
        self.lesson = Lesson.objects.create(id="l1", course=self.course, title="Lesson", topic="python")
        self.user = User.objects.create(id="u1", name="User", role="student")
        self.blueprint = QuizBlueprint.objects.create(
            id="bp1",
            lesson=self.lesson,
            rules={"count": 2, "difficulty": [1, 3], "mix": True}
        )

        # Создаем несколько заданий
        for i in range(1, 6):
            Item.objects.create(
                id=f"item{i}",
                lesson=self.lesson,
                type="mcq/single",
                stem=f"Question {i}",
                options=["A", "B", "C"],
                answer=[0],
                tags=["python"],
                difficulty=i  # Сложности от 1 до 5
            )

    def test_1_immutable_data_loading(self):
        """Тест 1: Загрузка в иммутабельные структуры"""
        courses, items, blueprints, users = load_immutable_data()

        # Проверяем кортежи
        self.assertIsInstance(items, tuple)
        self.assertTrue(all(isinstance(item, ImmutableItem) for item in items))

        # Проверяем преобразование списков в кортежи
        sample_item = items[0]
        self.assertIsInstance(sample_item.options, tuple)

    def test_2_pick_items_uses_filter(self):
        """Тест 2: pick_items использует filter"""
        _, items, blueprints, _ = load_immutable_data()
        bp = blueprints[0]  # difficulty [1,3]

        selected = pick_items_functional(items, bp)

        # FILTER: должны быть только задания сложности 1-3
        self.assertTrue(all(1 <= item.difficulty <= 3 for item in selected))

    def test_3_calculate_statistics_uses_reduce(self):
        """Тест 3: calculate_statistics использует reduce"""
        stats = calculate_statistics()

        # REDUCE: проверяем агрегаты
        self.assertEqual(stats['total_items'], 5)
        self.assertIn('mcq/single', stats['type_distribution'])  # REDUCE сработал

    def test_4_sum_score_uses_reduce(self):
        """Тест 4: sum_score использует reduce"""
        quiz = Quiz.objects.create(id="q1", user=self.user, blueprint=self.blueprint, status="started")
        Grade.objects.create(id="g1", quiz=quiz, score=5.0, breakdown=[])
        Grade.objects.create(id="g2", quiz=quiz, score=3.0, breakdown=[])

        grades = tuple(Grade.objects.all())
        total = sum_score(grades)

        # REDUCE: 5.0 + 3.0 = 8.0
        self.assertEqual(total, 8.0)

    def test_5_hof_filter_factory(self):
        """Тест 5: Функции высшего порядка"""
        _, items, _, _ = load_immutable_data()

        # HOF: создаем функцию-фильтр
        filter_func = create_filter_factory(difficulty_range=(2, 4))
        filtered = apply_filters(items, filter_func)

        self.assertTrue(all(2 <= item.difficulty <= 4 for item in filtered))

    def test_6_ui_overview_works(self):
        """Тест 6: UI Overview агрегаты работают"""
        stats = calculate_statistics()

        # Проверяем что все данные для UI есть
        self.assertIn('total_courses', stats)
        self.assertIn('total_items', stats)
        self.assertIn('type_distribution', stats)
        self.assertIn('difficulty_distribution', stats)

        # Проверяем распределения (сделаны через reduce)
        self.assertIsInstance(stats['type_distribution'], dict)
        self.assertIsInstance(stats['difficulty_distribution'], dict)