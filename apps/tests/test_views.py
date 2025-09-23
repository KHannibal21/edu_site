# from django.test import TestCase, Client
# from django.urls import reverse
# from apps.models import *
#
#
# class ViewTests(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.course = Course.objects.create(id="c1", title="Course", topics=[])
#         self.lesson = Lesson.objects.create(id="l1", course=self.course, title="Lesson", topic="test")
#         self.user = User.objects.create(id="u1", name="User", role="student")
#         self.blueprint = QuizBlueprint.objects.create(id="bp1", lesson=self.lesson, rules={})
#
#     def test_overview_view(self):
#         """Тест главной страницы"""
#         response = self.client.get(reverse('apps:overview'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'apps/overview.html')  # ← исправлено
#
#     def test_data_view(self):
#         """Тест страницы данных"""
#         response = self.client.get(reverse('apps:data'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'apps/data.html')  # ← исправлено
#
#     def test_functional_view(self):
#         """Тест страницы функционального ядра"""
#         response = self.client.get(reverse('apps:functional'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'apps/functional.html')  # ← исправлено
#
#     def test_quiz_detail_view(self):
#         """Тест страницы деталей квиза"""
#         # Сначала создаем квиз
#         quiz = Quiz.objects.create(
#             id="quiz_test",
#             user=self.user,
#             blueprint=self.blueprint,
#             status="started"
#         )
#
#         response = self.client.get(reverse('apps:quiz_detail', args=[quiz.id]))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'apps/quiz_detail.html')  # ← исправлено
#
#     def test_generate_quiz_ajax(self):
#         """Тест AJAX endpoint"""
#         response = self.client.post(reverse('apps:generate_quiz'), {
#             'user_id': self.user.id,
#             'blueprint_id': self.blueprint.id,
#         })
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('success', response.json())