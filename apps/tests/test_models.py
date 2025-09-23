# from django.test import TestCase
# from apps.models import *
#
#
# class ModelTests(TestCase):
#     def test_course_creation(self):
#         """Тест создания курса"""
#         course = Course.objects.create(
#             id="test_course",
#             title="Test Course",
#             topics=["python", "test"]
#         )
#         self.assertEqual(course.title, "Test Course")
#         self.assertIn("python", course.topics)
#
#     def test_item_creation(self):
#         """Тест создания задания"""
#         course = Course.objects.create(id="c1", title="Course", topics=[])
#         lesson = Lesson.objects.create(id="l1", course=course, title="Lesson", topic="test")
#
#         item = Item.objects.create(
#             id="item1",
#             lesson=lesson,
#             type="mcq/single",
#             stem="Test question?",
#             options=["A", "B", "C"],
#             answer=[0],
#             tags=["test"],
#             difficulty=3
#         )
#
#         self.assertEqual(item.type, "mcq/single")
#         self.assertEqual(item.difficulty, 3)
#
#     def test_quiz_creation(self):
#         """Тест создания квиза"""
#         course = Course.objects.create(id="c1", title="Course", topics=[])
#         lesson = Lesson.objects.create(id="l1", course=course, title="Lesson", topic="test")
#         user = User.objects.create(id="u1", name="User", role="student")
#         blueprint = QuizBlueprint.objects.create(id="bp1", lesson=lesson, rules={})
#
#         quiz = Quiz.objects.create(
#             id="quiz1",
#             user=user,
#             blueprint=blueprint,
#             ts="2024-01-01T00:00:00Z",
#             status="started"
#         )
#
#         self.assertEqual(quiz.status, "started")
#         self.assertEqual(quiz.user.role, "student")