from django.test import TestCase
from apps.models import *
from apps.services import *
from apps.recursion import *


class Lab2Test(TestCase):
    """6 тестов для лабы №2: Замыкания и рекурсия"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.course = Course.objects.create(
            id="course1", title="Python Course", topics=["python", "programming"]
        )
        self.lesson1 = Lesson.objects.create(
            id="lesson1", course=self.course, title="Python Basics", topic="python"
        )
        self.lesson2 = Lesson.objects.create(
            id="lesson2", course=self.course, title="Python Advanced", topic="python"
        )

        # Создаем задания с разными тегами и сложностью
        self.items = []
        for i in range(1, 6):
            item = Item.objects.create(
                id=f"item{i}",
                lesson=self.lesson1,
                type="mcq/single" if i % 2 == 0 else "mcq/multi",
                stem=f"Question {i}",
                options=["A", "B", "C"],
                answer=[0],
                tags=["python", "basic" if i < 3 else "advanced"],
                difficulty=i
            )
            self.items.append(item)

        self.blueprint = QuizBlueprint.objects.create(
            id="bp1",
            lesson=self.lesson1,
            rules={
                "count": 10,
                "difficulty": [2, 4],
                "filters": {
                    "topics": ["python"],
                    "types": ["mcq/single"]
                },
                "settings": {
                    "time_limit": 30,
                    "randomize": True
                }
            }
        )

    # ТЕСТ 1: Замыкания-фильтры
    def test_closure_filters(self):
        """Тест 1: Замыкания-фильтры работают корректно"""
        _, items, _, _ = load_immutable_data()

        # Создаем фильтры через замыкания
        python_filter = by_topic("python")
        difficulty_filter = by_difficulty(2, 4)
        type_filter = by_type("mcq/single")

        # Применяем фильтры
        python_items = tuple(filter(python_filter, items))
        difficulty_items = tuple(filter(difficulty_filter, items))
        type_items = tuple(filter(type_filter, items))

        # Проверяем результаты
        self.assertTrue(all("python" in item.tags for item in python_items))
        self.assertTrue(all(2 <= item.difficulty <= 4 for item in difficulty_items))
        self.assertTrue(all(item.type == "mcq/single" for item in type_items))

    # ТЕСТ 2: Композитный фильтр через замыкания
    def test_composite_closure_filter(self):
        """Тест 2: Композиция фильтров через замыкания"""
        _, items, _, _ = load_immutable_data()

        # Создаем композитный фильтр
        composite = create_composite_filter(
            by_topic("python"),
            by_difficulty(2, 4),
            by_type("mcq/single")
        )

        filtered_items = tuple(filter(composite, items))

        # Все условия должны выполняться
        self.assertTrue(all(
            "python" in item.tags and
            2 <= item.difficulty <= 4 and
            item.type == "mcq/single"
            for item in filtered_items
        ))

    # ТЕСТ 3: Рекурсия - flatten_curriculum
    def test_flatten_curriculum_recursion(self):
        """Тест 3: Рекурсивное преобразование иерархии курсов"""
        courses = tuple(Course.objects.all())
        lessons = tuple(Lesson.objects.all())

        result = flatten_curriculum(courses, lessons)

        # Проверяем структуру результата
        self.assertIsInstance(result, tuple)
        self.assertTrue(all(isinstance(pair, tuple) for pair in result))
        self.assertTrue(all(len(pair) == 2 for pair in result))

        # Должны быть пары (курс, урок)
        self.assertIn(("Python Course", "Python Basics"), result)
        self.assertIn(("Python Course", "Python Advanced"), result)

    # ТЕСТ 4: Рекурсия - build_item_tree
    def test_build_item_tree_recursion(self):
        """Тест 4: Рекурсивное построение дерева заданий"""
        _, items, _, _ = load_immutable_data()

        tree_result = build_item_tree(items, "python")

        # Проверяем структуру дерева
        self.assertIsInstance(tree_result, tuple)
        if tree_result:
            tree = tree_result[0]
            self.assertIn('topic', tree)
            self.assertIn('items_count', tree)
            self.assertIn('subtopics', tree)

            # Рекурсивно проверяем подсчет элементов
            total_count = count_items_in_tree(tree)
            self.assertGreaterEqual(total_count, 0)

    # ТЕСТ 5: Рекурсия - walk_blueprint_rules
    def test_walk_blueprint_rules_recursion(self):
        """Тест 5: Рекурсивный обход вложенных правил"""
        rules = {
            "count": 10,
            "filters": {
                "topics": ["python", "web"],
                "difficulty": [2, 4]
            },
            "settings": {
                "time_limit": 30,
                "randomize": True
            }
        }

        result = walk_blueprint_rules(rules)

        # Проверяем развертку правил
        self.assertIsInstance(result, tuple)
        self.assertTrue(all(isinstance(pair, tuple) for pair in result))

        # Должны найти все ключи
        flat_keys = [key for key, value in result]
        self.assertIn("count", flat_keys)
        self.assertIn("filters.topics[0]", flat_keys)
        self.assertIn("settings.time_limit", flat_keys)

    # ТЕСТ 6: Конфигураторы через замыкания
    def test_closure_configurators(self):
        """Тест 6: Замыкания-конфигураторы"""
        # Тестируем конфигуратор квизов
        configurator = quiz_configurator(base_count=15)
        config = configurator(difficulty_range=(2, 5), time_limit=45)

        self.assertEqual(config['count'], 15)
        self.assertEqual(config['difficulty_range'], (2, 5))
        self.assertEqual(config['time_limit'], 45)

        # Тестируем предустановки сложности
        easy_preset = difficulty_preset('easy')
        hard_preset = difficulty_preset('hard')

        self.assertEqual(easy_preset(), (1, 2))
        self.assertEqual(hard_preset(), (4, 5))