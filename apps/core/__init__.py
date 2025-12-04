"""
Functional Core Module
Иммутабельные модели и чистые функции для системы тестирования
"""

from .models import *
from .transforms import *
from .filters import *
from .recursion import *
from .variants import *
from .containers import *
from .validation import *
from .lazy import *
from .events import *
from .composition import *
from .async_ops import *
from .utils import *
from .services import *

__version__ = "1.0.0"
__all__ = [
    # Models
    "Item", "Course", "Lesson", "User", "QuizBlueprint",
    "Quiz", "Answer", "Grade", "Rule",
    # Functions
    "load_seed", "pick_items", "start_quiz", "sum_score",
    "by_topic", "by_difficulty", "by_type", "with_tags",
    "flatten_curriculum", "walk_blueprint_rules",
    "generate_quiz_variant",
    # Containers
    "Maybe", "Either",
    # Lazy
    "iter_answers", "lazy_grade_stream",
    # Events
    "Event", "EventBus",
    # Composition
    "compose", "pipe", "QuizService", "GradeService", "ReportService",
    # Async
    "generate_variants_batch", "grade_submissions_batch"
]