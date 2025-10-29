import pytest
from apps.models import Item, Quiz, User, QuizBlueprint, Answer, GradingRule, Grade
from apps.services import iter_answers, lazy_grade_stream, process_quiz_grading, calculate_score
from collections.abc import Iterator, Generator
import time


@pytest.fixture
def setup_lazy_data(db):
    """Создаем данные для тестов ленивых вычислений"""
    user = User.objects.create(id="lazy_user", name="Lazy User", role="student")

    blueprint = QuizBlueprint.objects.create(
        id="lazy_bp",
        rules={"count": 5, "difficulty": [1, 5], "mix": True}
    )

    quiz = Quiz.objects.create(
        id="lazy_quiz",
        user=user,
        blueprint=blueprint,
        status="finished"
    )

    # Создаем тестовые задания - ЧЕТКО задаем типы
    items = []
    item_data = [
        {"id": "lazy_item1", "type": "mcq/multi", "answer": [0, 1], "difficulty": 1},
        {"id": "lazy_item2", "type": "mcq/single", "answer": [0], "difficulty": 2},
        {"id": "lazy_item3", "type": "mcq/multi", "answer": [0, 1], "difficulty": 3},
        {"id": "lazy_item4", "type": "mcq/single", "answer": [0], "difficulty": 4},
        {"id": "lazy_item5", "type": "mcq/multi", "answer": [0, 1], "difficulty": 5},
    ]

    for data in item_data:
        item = Item.objects.create(
            id=data["id"],
            type=data["type"],
            stem=f"Lazy Question {data['id']}",
            options=["Option A", "Option B", "Option C", "Option D"],
            answer=data["answer"],
            tags=["python", "lazy"],
            difficulty=data["difficulty"]
        )
        items.append(item)
        quiz.items.add(item)

    # Создаем правила оценивания
    single_rule = GradingRule.objects.create(
        id="test_single",
        item_type="mcq/single",
        name="Single Choice Rule",
        scoring_function="exact_match",
        weight=1.0,
        parameters={}
    )

    multi_rule = GradingRule.objects.create(
        id="test_multi",
        item_type="mcq/multi",
        name="Multi Choice Rule",
        scoring_function="partial",
        weight=1.5,
        parameters={"penalty_per_wrong": 0.25}
    )

    # Создаем ответы - ЧЕТКО задаем какие правильные/неправильные
    answers = []
    answer_data = [
        {"item_id": "lazy_item1", "payload": [0, 1], "correct": True},  # multi, правильный
        {"item_id": "lazy_item2", "payload": [0], "correct": True},  # single, правильный
        {"item_id": "lazy_item3", "payload": [2, 3], "correct": False},  # multi, неправильный
        {"item_id": "lazy_item4", "payload": [1], "correct": False},  # single, неправильный
        {"item_id": "lazy_item5", "payload": [0, 1], "correct": True},  # multi, правильный
    ]

    for data in answer_data:
        item = next(i for i in items if i.id == data["item_id"])
        answer = Answer.objects.create(
            id=f"lazy_answer_{data['item_id']}",
            quiz=quiz,
            item=item,
            payload=data["payload"],
            is_graded=False
        )
        answers.append(answer)

    return user, blueprint, quiz, items, answers, {"mcq/single": single_rule, "mcq/multi": multi_rule}


def test_iter_answers_returns_iterator(setup_lazy_data):
    """Тест 1: iter_answers возвращает итератор"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    result = iter_answers(Answer.objects.all())

    assert isinstance(result, Iterator)
    answers_list = list(result)
    assert len(answers_list) == 5


def test_iter_answers_with_predicate_filters_correctly(setup_lazy_data):
    """Тест 2: iter_answers с предикатом фильтрует результаты"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    # Фильтруем только single-choice ответы
    predicate = lambda a: a.item.type == "mcq/single"
    filtered_answers = list(iter_answers(Answer.objects.all(), predicate))

    # Должно быть 2 single-choice вопроса: lazy_item2 и lazy_item4
    assert len(filtered_answers) == 2
    for answer in filtered_answers:
        assert answer.item.type == "mcq/single"


def test_lazy_grade_stream_uses_generators(setup_lazy_data):
    """Тест 3: lazy_grade_stream использует генераторы (yield)"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    stream = lazy_grade_stream(answers, rules)

    assert isinstance(stream, Iterator)
    assert isinstance(stream, Generator)

    results = list(stream)
    assert len(results) == 5


def test_lazy_grade_stream_correct_scoring(setup_lazy_data):
    """Тест 4: lazy_grade_stream правильно вычисляет оценки"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    stream = lazy_grade_stream(answers, rules)
    results = dict(stream)

    assert len(results) == 5

    # Проверяем конкретные оценки на основе наших данных:
    # lazy_item1: multi, правильный [0,1] → 1.0 * 1.5 = 1.5
    # lazy_item2: single, правильный [0] → 1.0 * 1.0 = 1.0
    # lazy_item3: multi, неправильный [2,3] → 0.0 * 1.5 = 0.0
    # lazy_item4: single, неправильный [1] → 0.0 * 1.0 = 0.0
    # lazy_item5: multi, правильный [0,1] → 1.0 * 1.5 = 1.5

    assert results["lazy_item1"] == 1.5
    assert results["lazy_item2"] == 1.0
    assert results["lazy_item3"] == 0.0
    assert results["lazy_item4"] == 0.0
    assert results["lazy_item5"] == 1.5


def test_process_quiz_grading_materializes_at_end(setup_lazy_data):
    """Тест 5: process_quiz_grading материализует результаты только в конце"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    result = process_quiz_grading(quiz, top_k=2)

    # Проверяем что топ-K работает
    assert 'hardest_items' in result
    assert len(result['hardest_items']) <= 2

    # Проверяем что вся статистика материализована в конце
    assert 'difficulty_stats' in result
    assert 'total_score' in result
    assert 'percentage' in result
    assert 'items_attempted' in result

    # Проверяем корректность вычислений
    assert result['items_attempted'] == 5
    # Общий балл: 1.5 + 1.0 + 0.0 + 0.0 + 1.5 = 4.0
    assert result['total_score'] == 4.0


def test_calculate_score_functions_correctly(setup_lazy_data):
    """Тест 6: функции calculate_score работают корректно для разных типов"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    single_rule = rules["mcq/single"]
    multi_rule = rules["mcq/multi"]

    # Тестируем exact_match (single choice)
    score_correct_single = calculate_score([0], [0], single_rule)
    score_wrong_single = calculate_score([1], [0], single_rule)

    # Тестируем partial (multi choice)
    score_all_correct = calculate_score([0, 1], [0, 1], multi_rule)
    score_partial_correct = calculate_score([0, 2], [0, 1], multi_rule)  # 1 прав, 1 неправ
    score_all_wrong = calculate_score([2, 3], [0, 1], multi_rule)

    assert score_correct_single == 1.0
    assert score_wrong_single == 0.0
    assert score_all_correct == 1.0
    # Для partial: (1 правильный - 1 неправильный * 0.25) / 2 правильных = (1 - 0.25) / 2 = 0.375
    assert score_partial_correct == 0.375
    assert score_all_wrong == 0.0


def test_debug_data(setup_lazy_data):
    """Тест для отладки - можно удалить после исправления"""
    user, blueprint, quiz, items, answers, rules = setup_lazy_data

    print("\n=== DEBUG DATA ===")
    print(f"Всего items: {len(items)}")
    for i, item in enumerate(items):
        print(f"Item {i}: id={item.id}, type={item.type}, answer={item.answer}")

    print(f"\nВсего answers: {len(answers)}")
    for i, answer in enumerate(answers):
        print(f"Answer {i}: item_id={answer.item.id}, payload={answer.payload}")

    single_count = len([item for item in items if item.type == "mcq/single"])
    multi_count = len([item for item in items if item.type == "mcq/multi"])
    print(f"\nSingle-choice: {single_count}, Multi-choice: {multi_count}")

    # Проверим оценки вручную
    stream = lazy_grade_stream(answers, rules)
    results = dict(stream)
    print(f"\nРеальные оценки: {results}")