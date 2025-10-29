import time
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import *
from .recursion import flatten_curriculum, build_item_tree, walk_blueprint_rules
from .memo import generate_quiz_variant, benchmark_generation
from .services import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


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


def login_view(request):
    """Страница входа"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('apps:overview')
        else:
            messages.error(request, "Неверное имя пользователя или пароль")
    return render(request, 'apps/login.html', {'menu': ''})


def register_view(request):
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Пароли не совпадают")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            return redirect('apps:overview')

    return render(request, 'apps/register.html', {'menu': ''})




def functional_core(request):
    """Демонстрация функционального ядра"""
    courses, items, blueprints, users = load_immutable_data()
    student_users = [user for user in users if user.role == 'student']

    # Демонстрация Maybe/Either с реальными операциями
    functional_patterns_demo = None

    if request.method == 'POST' and 'demo_maybe_either' in request.POST:
        # Демонстрация Maybe
        item_id = request.POST.get('item_id', 'item_1')
        maybe_result = safe_item(items, item_id)

        # Демонстрация Either с валидацией ответа
        answer_payload = request.POST.get('answer_payload', '')

        # Простой парсинг без JSON - для MCQ это индексы, для short - текст
        answer_data = answer_payload
        if answer_payload.startswith('[') and answer_payload.endswith(']'):
            # Простая обработка формата [0,1] без json
            try:
                # Убираем скобки и разбиваем по запятым
                numbers = answer_payload[1:-1].split(',')
                answer_data = [int(num.strip()) for num in numbers if num.strip()]
            except:
                answer_data = answer_payload

        selected_item = maybe_result.get_or_else(items[0] if items else None)

        if selected_item:
            validation_result = validate_answer(selected_item, answer_data, ())
            grading_result = grade_item(selected_item, answer_data, ())

            functional_patterns_demo = {
                'item_id': item_id,
                'maybe_result': maybe_result,
                'validation_result': validation_result,
                'grading_result': grading_result,
                'selected_item': selected_item,
                'user_answer': answer_payload
            }
        else:
            functional_patterns_demo = {
                'item_id': item_id,
                'maybe_result': maybe_result,
                'user_answer': answer_payload
            }

    if request.method == 'POST' and 'user_id' in request.POST:
        user_id = request.POST.get('user_id')
        blueprint_id = request.POST.get('blueprint_id')

        user = User.objects.get(id=user_id)
        blueprint = QuizBlueprint.objects.get(id=blueprint_id)
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
        'functional_patterns_demo': functional_patterns_demo,
        'all_items': items[:10],  # Показываем первые 10 для демонстрации
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
    form_data = {'pool_size': 50, 'bp_key': 'bp_10:python:1,2,3:42'}  # ← ДОБАВЛЯЕМ ДАННЫЕ ФОРМЫ

    if request.method == 'POST':
        if 'run_benchmark' in request.POST:
            iterations = int(request.POST.get('iterations', 100))
            pool_size = int(request.POST.get('benchmark_pool_size', 200))
            benchmark_results = benchmark_generation(iterations, pool_size)

        elif 'generate_variant' in request.POST:
            bp_key = request.POST.get('bp_key', 'bp_10:python:1,2,3:42')
            pool_size = int(request.POST.get('pool_size', 50))

            # СОХРАНЯЕМ ВВЕДЕННЫЕ ДАННЫЕ
            form_data['pool_size'] = pool_size  # ← СОХРАНЯЕМ ВВЕДЕННОЕ ЗНАЧЕНИЕ
            form_data['bp_key'] = bp_key  # ← СОХРАНЯЕМ ВВЕДЕННЫЙ BP_KEY

            # Создаем тестовый пул
            pool_idx = tuple(f"item_{i}diff{random.randint(1, 5)}" for i in range(pool_size))

            # Генерируем вариант (с кэшем)
            start_time = time.time()
            variant = generate_quiz_variant(bp_key, pool_idx, 42)
            generation_time = time.time() - start_time

            cache_demo = {
                'bp_key': bp_key,
                'pool_size': pool_size,
                'variant': variant,
                'generation_time': round(generation_time, 4),
                'cache_info': generate_quiz_variant.cache_info()
            }

    context = {
        'benchmark_results': benchmark_results,
        'cache_demo': cache_demo,
        'form_data': form_data,  # ← ПЕРЕДАЕМ ДАННЫЕ ФОРМЫ В ШАБЛОН
        'menu': 'reports'
    }
    return render(request, 'apps/reports.html', context)