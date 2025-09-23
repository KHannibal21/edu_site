from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from .services import *


def overview(request):
    """Главная страница с обзором статистики"""
    stats = calculate_statistics()

    context = {
        'stats': stats,
        'menu': 'overview'
    }
    return render(request, 'apps/overview.html', context)


def data_explorer(request):
    """Просмотр данных"""
    courses = Course.objects.all()
    lessons = Lesson.objects.all()
    items = Item.objects.all()
    users = User.objects.all()
    blueprints = QuizBlueprint.objects.all()

    # Фильтрация
    difficulty_filter = request.GET.get('difficulty', '')
    type_filter = request.GET.get('type', '')

    if difficulty_filter:
        items = items.filter(difficulty=int(difficulty_filter))
    if type_filter:
        items = items.filter(type=type_filter)

    context = {
        'courses': courses,
        'lessons': lessons,
        'items': items[:50],
        'users': users,
        'blueprints': blueprints,
        'menu': 'data',
        'difficulty_filter': difficulty_filter,
        'type_filter': type_filter,
    }
    return render(request, 'apps/data.html', context)


def functional_core(request):
    """Демонстрация функционального ядра"""
    courses, items, blueprints, users = load_immutable_data()
    student_users = [user for user in users if user.role == 'student']

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        blueprint_id = request.POST.get('blueprint_id')

        user = User.objects.get(id=user_id)
        blueprint = QuizBlueprint.objects.get(id=blueprint_id)

        # Создаем квиз функциональным способом
        quiz = create_quiz_functional(user, blueprint, items)

        return redirect('apps:quiz_detail', quiz_id=quiz.id)

    # Демонстрация фильтров
    demo_filters = {
        'difficulty_range': (2, 4),
        'types': ('mcq/single', 'mcq/multi')
    }
    filter_func = create_filter_factory(**demo_filters)
    filtered_items = apply_filters(items, filter_func)

    context = {
        'student_users': student_users,
        'blueprints': blueprints,
        'demo_items_count': len(filtered_items),
        'menu': 'functional'
    }
    return render(request, 'apps/functional.html', context)


def quiz_detail(request, quiz_id):
    """Детальная страница квиза"""
    quiz = Quiz.objects.get(id=quiz_id)
    items = quiz.items.all()

    context = {
        'quiz': quiz,
        'items': items,
        'menu': 'functional'
    }
    return render(request, 'apps/quiz_detail.html', context)


def generate_quiz_ajax(request):
    """AJAX endpoint для генерации квиза"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            blueprint_id = request.POST.get('blueprint_id')

            user = User.objects.get(id=user_id)
            blueprint = QuizBlueprint.objects.get(id=blueprint_id)
            _, items, _, _ = load_immutable_data()

            quiz = create_quiz_functional(user, blueprint, items)

            return JsonResponse({
                'success': True,
                'quiz_id': quiz.id,
                'items_count': quiz.items.count()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })