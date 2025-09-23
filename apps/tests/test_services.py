# from django.test import TestCase
# from apps.models import *
# from apps.services import *
#
#
# class FunctionalServicesTest(TestCase):
#     def setUp(self):
#         """Настройка тестовых данных"""
#         self.course = Course.objects.create(
#             id="course1", title="Test Course", topics=["python", "test"]
#         )
#         self.lesson = Lesson.objects.create(
#             id="lesson1", course=self.course, title="Test Lesson", topic="python"
#         )
#         self.user = User.objects.create(
#             id="user1", name="Test User", role="student"
#         )
#         self.teacher = User.objects.create(
#             id="teacher1", name="Test Teacher", role="teacher"
#         )
#
#         # Создаем задания с разной сложностью
#         difficulties = [1, 2, 3, 4, 5, 2, 3, 4]
#         for i, diff in enumerate(difficulties):
#             Item.objects.create(
#                 id=f"item{i + 1}",
#                 lesson=self.lesson,
#                 type="mcq/single",
#                 stem=f"Question {i + 1}",
#                 options=["A", "B", "C"],
#                 answer=[0],
#                 tags=["python"],
#                 difficulty=diff
#             )
#
#         self.blueprint = QuizBlueprint.objects.create(
#             id="bp1", lesson=self.lesson, rules={"count": 3, "difficulty": [2, 4], "mix": True}
#         )
#
#     def test_calculate_statistics(self):
#         """Тест расчета статистики с reduce и словарями"""
#         stats = calculate_statistics()
#
#         # Проверяем основные метрики
#         self.assertEqual(stats['total_courses'], 1)
#         self.assertEqual(stats['total_lessons'], 1)
#         self.assertEqual(stats['total_items'], 8)
#         self.assertEqual(stats['total_users'], 2)
#
#         # Проверяем словарь распределения по типам
#         self.assertIsInstance(stats['type_distribution'], dict)
#         self.assertIn('mcq/single', stats['type_distribution'])
#         self.assertEqual(stats['type_distribution']['mcq/single'], 8)
#
#         # Проверяем словарь распределения по сложности
#         self.assertIsInstance(stats['difficulty_distribution'], dict)
#         self.assertEqual(stats['difficulty_distribution'][2], 2)  # Два задания сложности 2
#         self.assertEqual(stats['difficulty_distribution'][3], 2)  # Два задания сложности 3
#
#         # Проверяем кортеж уникальных тегов
#         self.assertIsInstance(stats['unique_tags'], tuple)
#         self.assertIn('python', stats['unique_tags'])
#
#     def test_filter_items_by_difficulty_with_tuple(self):
#         """Тест фильтрации с кортежами"""
#         _, items, _, _ = load_immutable_data()
#
#         # Используем кортеж для диапазона сложности
#         filtered = filter_items_by_difficulty(items, (2, 4))
#
#         # Проверяем что возвращается кортеж
#         self.assertIsInstance(filtered, tuple)
#         self.assertEqual(len(filtered), 6)  # 2,3,4,2,3,4
#         self.assertTrue(all(2 <= item.difficulty <= 4 for item in filtered))
#
#     def test_pick_items_functional_with_hof(self):
#         """Тест функционального выбора с HOF"""
#         _, items, blueprints, _ = load_immutable_data()
#         bp = blueprints[0]
#
#         selected = pick_items_functional(items, bp)
#
#         # Проверяем иммутабельные структуры
#         self.assertIsInstance(selected, tuple)
#         self.assertEqual(len(selected), 3)
#         self.assertTrue(all(2 <= item.difficulty <= 4 for item in selected))
#
#     def test_create_filter_factory_hof(self):
#         """Тест фабрики функций (HOF)"""
#         _, items, _, _ = load_immutable_data()
#
#         # Создаем функцию-фильтр через HOF
#         filter_func = create_filter_factory(difficulty_range=(3, 5))
#         self.assertTrue(callable(filter_func))  # Проверяем что это функция
#
#         # Применяем фильтр
#         filtered = apply_filters(items, filter_func)
#         self.assertTrue(all(3 <= item.difficulty <= 5 for item in filtered))
#
#     def test_immutable_structures(self):
#         """Тест иммутабельных структур данных"""
#         courses, items, blueprints, users = load_immutable_data()
#
#         # Проверяем кортежи
#         self.assertIsInstance(courses, tuple)
#         self.assertIsInstance(items, tuple)
#         self.assertIsInstance(blueprints, tuple)
#         self.assertIsInstance(users, tuple)
#
#         # Проверяем иммутабельные объекты
#         self.assertTrue(all(isinstance(item, ImmutableItem) for item in items))
#         self.assertTrue(all(isinstance(course, ImmutableCourse) for course in courses))
#
#         # Проверяем что списки преобразованы в кортежи
#         sample_item = items[0]
#         self.assertIsInstance(sample_item.options, tuple)
#         self.assertIsInstance(sample_item.tags, tuple)
#
#     def test_sum_score_reduce(self):
#         """Тест reduce функции с кортежами"""
#         quiz = Quiz.objects.create(id="quiz1", user=self.user, blueprint=self.blueprint, status="started")
#         Grade.objects.create(id="grade1", quiz=quiz, score=5.0, breakdown=[])
#         Grade.objects.create(id="grade2", quiz=quiz, score=3.0, breakdown=[])
#         Grade.objects.create(id="grade3", quiz=quiz, score=2.0, breakdown=[])
#
#         # Создаем кортеж оценок
#         grades = tuple(Grade.objects.all())
#         self.assertIsInstance(grades, tuple)
#
#         # Тестируем reduce
#         total = sum_score(grades)
#         self.assertEqual(total, 10.0)
#
#     def test_list_operations_in_models(self):
#         """Тест операций со списками в моделях"""
#         course = Course.objects.create(
#             id="course_list",
#             title="Course with Lists",
#             topics=["python", "django", "web"]  # ← список
#         )
#
#         # Проверяем операции со списками
#         self.assertIsInstance(course.topics, list)
#         self.assertEqual(len(course.topics), 3)
#         self.assertIn("python", course.topics)
#
#         item = Item.objects.create(
#             id="item_list",
#             lesson=self.lesson,
#             type="mcq/single",
#             stem="Test question?",
#             options=["A", "B", "C", "D"],  # ← список
#             answer=[0, 2],  # ← список
#             tags=["test", "easy", "quick"],  # ← список
#             difficulty=3
#         )
#
#         # Проверяем списки в JSON полях
#         self.assertIsInstance(item.options, list)
#         self.assertIsInstance(item.answer, list)
#         self.assertIsInstance(item.tags, list)
#         self.assertEqual(len(item.options), 4)
#
#     def test_dictionary_operations(self):
#         """Тест операций со словарями"""
#         blueprint = QuizBlueprint.objects.create(
#             id="bp_dict",
#             lesson=self.lesson,
#             rules={  # ← словарь
#                 "count": 10,
#                 "difficulty": [1, 5],
#                 "topics": ["python", "test"],  # ← список в словаре
#                 "types": ["mcq/single", "mcq/multi"],  # ← список в словаре
#                 "mix": True
#             }
#         )
#
#         # Проверяем словарь
#         self.assertIsInstance(blueprint.rules, dict)
#         self.assertEqual(blueprint.rules["count"], 10)
#         self.assertIsInstance(blueprint.rules["topics"], list)
#         self.assertIn("python", blueprint.rules["topics"])
#
#     def test_set_operations_for_uniqueness(self):
#         """Тест операций с множествами для уникальности"""
#         _, items, _, _ = load_immutable_data()
#
#         # Создаем множество ID для проверки уникальности
#         item_ids = set(item.id for item in items)
#         self.assertIsInstance(item_ids, set)
#         self.assertEqual(len(item_ids), len(items))  # Все ID должны быть уникальны
#
#         # Тестируем объединение множеств тегов
#         all_tags = set()
#         for item in items:
#             all_tags.update(item.tags)
#
#         self.assertIsInstance(all_tags, set)
#         self.assertIn("python", all_tags)
#
#
# class IntegrationTest(TestCase):
#     """Интеграционные тесты полного потока"""
#
#     def test_full_quiz_creation_flow_with_collections(self):
#         """Полный тест потока создания квиза с различными структурами данных"""
#         # Создаем тестовые данные
#         course = Course.objects.create(
#             id="c1",
#             title="Course",
#             topics=["python", "programming"]  # ← список
#         )
#         lesson = Lesson.objects.create(id="l1", course=course, title="Lesson", topic="test")
#         user = User.objects.create(id="u1", name="User", role="student")
#
#         # Создаем задания с различными структурами данных
#         items_data = [
#             {"type": "mcq/single", "options": ["A", "B"], "answer": [0], "tags": ["easy"], "difficulty": 1},
#             {"type": "mcq/multi", "options": ["A", "B", "C"], "answer": [0, 1], "tags": ["medium"], "difficulty": 3},
#             {"type": "short", "options": [], "answer": "ответ", "tags": ["hard"], "difficulty": 5},
#         ]
#
#         for i, data in enumerate(items_data):
#             Item.objects.create(
#                 id=f"item{i}",
#                 lesson=lesson,
#                 type=data["type"],
#                 stem=f"Q{i}",
#                 options=data["options"],  # ← список
#                 answer=data["answer"],
#                 tags=data["tags"],  # ← список
#                 difficulty=data["difficulty"]
#             )
#
#         blueprint = QuizBlueprint.objects.create(
#             id="bp1",
#             lesson=lesson,
#             rules={  # ← словарь
#                 "count": 2,
#                 "mix": True,
#                 "difficulty": [1, 5]
#             }
#         )
#
#         # Тестируем весь функциональный поток
#         _, items, blueprints, _ = load_immutable_data()
#         bp_obj = blueprints[0]
#
#         # Применяем функциональные фильтры
#         selected = pick_items_functional(items, bp_obj)
#
#         # Проверяем результаты
#         self.assertIsInstance(selected, tuple)  # ← кортеж
#         self.assertEqual(len(selected), 2)
#
#         # Проверяем что выбраны задания разной сложности (из-за mix=True)
#         difficulties = [item.difficulty for item in selected]
#         self.assertTrue(1 in difficulties or 5 in difficulties)