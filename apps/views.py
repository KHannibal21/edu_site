import time
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from .recursion import flatten_curriculum, build_item_tree, walk_blueprint_rules
from .memo import generate_quiz_variant, benchmark_generation
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


def pipelines_demo(request):
    """Демонстрация пайплайнов и композиции функций"""
    _, items, blueprints, users = load_immutable_data()

    pipeline_results = {}
    composition_demo = {}

    # Демонстрация готовых пайплайнов
    if request.method == 'POST':
        pipeline_type = request.POST.get('pipeline_type', 'basic')
        min_diff = int(request.POST.get('min_difficulty', 1))
        max_diff = int(request.POST.get('max_difficulty', 5))
        topic = request.POST.get('topic', '')
        qtype = request.POST.get('qtype', '')
        required_tags = request.POST.get('required_tags', '').split(',') if request.POST.get('required_tags') else []

        # Выбор пайплайна
        if pipeline_type == 'basic':
            pipeline = basic_pipeline
            filtered_items = tuple(filter(pipeline(
                min_difficulty=min_diff,
                max_difficulty=max_diff,
                qtype=qtype
            ), items))
            pipeline_results['type'] = 'Базовый пайплайн'
            pipeline_results['filters'] = f'Сложность: {min_diff}-{max_diff}, Тип: {qtype or "любой"}'

        elif pipeline_type == 'advanced':
            pipeline = advanced_pipeline
            filtered_items = tuple(filter(pipeline(
                min_difficulty=min_diff,
                max_difficulty=max_diff,
                topic=topic,
                required_tags=tuple(required_tags)
            ), items))
            pipeline_results['type'] = 'Продвинутый пайплайн'
            pipeline_results[
                'filters'] = f'Сложность: {min_diff}-{max_diff}, Тема: {topic or "любая"}, Теги: {", ".join(required_tags) or "любые"}'

        pipeline_results['count'] = len(filtered_items)
        pipeline_results['items'] = filtered_items[:10]  # Показываем первые 10

    # Демонстрация композиции функций
    try:
        # Композиция: загрузка → фильтрация → преобразование
        from functools import reduce

        # 1. Загрузка и преобразование
        loaded_items = items

        # 2. Цепочка фильтров через композицию
        def compose(*functions):
            return reduce(lambda f, g: lambda x: f(g(x)), functions)

        # Создаем композицию функций
        processing_pipeline = compose(
            lambda items: tuple(filter(by_difficulty(2, 4), items)),  # FILTER по сложности
            lambda items: tuple(filter(by_topic('python'), items)),  # FILTER по теме
            lambda items: tuple(map(lambda item: {  # MAP для преобразования
                'id': item.id,
                'type': item.type,
                'difficulty': item.difficulty,
                'tags': item.tags
            }, items)),
            lambda items: items[:5]  # LIMIT
        )

        composition_result = processing_pipeline(loaded_items)
        composition_demo = {
            'pipeline': 'Загрузка → Фильтр(сложность) → Фильтр(тема) → Преобразование → Лимит',
            'input_count': len(loaded_items),
            'output_count': len(composition_result),
            'result': composition_result
        }

    except Exception as e:
        composition_demo = {'error': str(e)}

    context = {
        'pipeline_results': pipeline_results,
        'composition_demo': composition_demo,
        'menu': 'pipelines'
    }
    return render(request, 'apps/pipelines.html', context)


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


def reports_view(request):
    """UI: Reports → Variants (cached)"""
    benchmark_results = None
    cache_demo = None

    if request.method == 'POST':
        if 'run_benchmark' in request.POST:
            iterations = int(request.POST.get('iterations', 100))
            benchmark_results = benchmark_generation(iterations)

        elif 'generate_variant' in request.POST:
            # Демонстрация генерации вариантов
            bp_key = request.POST.get('bp_key', 'bp_10:python:1,2,3:42')
            pool_size = int(request.POST.get('pool_size', 50))

            # Создаем тестовый пул
            pool_idx = tuple(f"item_{i}_diff_{random.randint(1, 5)}" for i in range(pool_size))

            # Генерируем вариант (с кэшем)
            start_time = time.time()
            variant = generate_quiz_variant(bp_key, pool_idx, 42)
            generation_time = time.time() - start_time

            cache_demo = {
                'bp_key': bp_key,
                'variant': variant,
                'generation_time': round(generation_time, 4),
                'cache_info': generate_quiz_variant.cache_info()
            }

    context = {
        'benchmark_results': benchmark_results,
        'cache_demo': cache_demo,
        'menu': 'reports'
    }
    return render(request, 'apps/reports.html', context)