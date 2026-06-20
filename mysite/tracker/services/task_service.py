import re
import logging
from django.db.models import Avg
from ..models import Task
from .ai_service import get_chat_completion, extract_json_from_text
from ..choices import get_required_grade, LEVEL_CHOICES
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

LEVEL_ORDER = [choice[0] for choice in LEVEL_CHOICES]  # ['explorer', 'builder', 'master']


def extract_student_code(task_text: str, student_solution: str) -> str:
    task_lines = set(task_text.splitlines())
    student_lines = [
        line for line in student_solution.splitlines()
        if line.strip()
        and line not in task_lines
        and not re.match(r'(pass|# TODO|___+)', line.strip())
    ]
    return "\n".join(student_lines)


def grade_solution(user, task) -> dict:
    task_content = task.description or task.title
    prompt = (
        f"Task:\n{task_content}\n\n"
        f"Solution:\n{task.solution}\n"
        f"Review this code briefly as a teacher. Give 2-3 bullet points only: what's good, what's wrong, how to improve. "
        f"Be concise. The last line must be exactly: Grade: X/5"
    )
    ai_content = get_chat_completion(user, prompt)

    grade_match = re.search(r"Grade[:：]?\s*(\d)\s*/\s*5\s*$", ai_content, re.IGNORECASE)
    grade = int(grade_match.group(1)) if grade_match else 0
    review_body = re.sub(
        r"Grade[:：]?\s*\d\s*/\s*5\s*$", "", ai_content, flags=re.IGNORECASE
    ).strip()

    return {
        "grade": grade,
        "review": f"{review_body}\n\nGrade: {grade}/5",
    }


def update_progress(user_track, grade: int):
    """
    Called after every completed task.
    - Checks if grade meets the threshold for current position
    - If yes: increments progress_score, checks for level-up at 15
    - If no: returns the weak topic so AI can generate reinforcement
    """
    required = get_required_grade(user_track.progress_score)

    if grade >= required:
        user_track.progress_score += 1

        # Check for level up
        if user_track.progress_score >= 15:
            current_idx = LEVEL_ORDER.index(user_track.current_level)
            if current_idx < len(LEVEL_ORDER) - 1:
                user_track.current_level = LEVEL_ORDER[current_idx + 1]
            user_track.progress_score = 0  # reset for next level

        user_track.save(update_fields=['progress_score', 'current_level'])
        return None  # no reinforcement needed
    else:
        user_track.save(update_fields=['progress_score', 'current_level'])
        return True  # signal that reinforcement is needed


def get_weak_topic(user_track) -> str:
    """Find the topic of the most recent failed task."""
    last_failed = Task.objects.filter(
        user_learning_track=user_track,
        grade__isnull=False,
    ).order_by("-id").first()

    if last_failed:
        return last_failed.weak_topic or last_failed.title or "the previous topic"
    return "the previous topic"


def get_task_history_context(user_track) -> str:
    tasks = Task.objects.filter(
        user_learning_track=user_track
    ).order_by("-id")[:5]

    avg_grade = Task.objects.filter(
        user_learning_track=user_track,
        grade__isnull=False
    ).aggregate(Avg("grade"))["grade__avg"] or 0

    lines = [f"Average Student Grade: {avg_grade:.1f}/5.0"]
    lines += [
        f"- Task ID: {t.id}, Title: {t.title or 'Unknown'}, Grade: {t.grade}/5"
        for t in tasks if t.grade is not None
    ]
    return "\n".join(lines)


def validate_task_structure(data: dict):
    required = {"title", "description", "task_code", "language"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"AI returned invalid task structure, missing fields: {missing}")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def generate_next_task_text(user, user_track, reinforcement_topic: str = None) -> dict:
    history_context = get_task_history_context(user_track)

    if reinforcement_topic:
        reinforcement_instruction = (
            f"IMPORTANT: The student struggled with '{reinforcement_topic}'. "
            f"Generate a reinforcement task focused specifically on that topic. "
            f"Make it slightly easier to rebuild confidence."
        )
    else:
        reinforcement_instruction = (
            "Analyze the Student Performance History. "
            "If average grades are high (4-5), increase task complexity. "
            "If grades are low (1-2), focus on simpler tasks. "
        )

    system_msg = (
        "You are a professional coding mentor. "
        "Return ONLY a JSON object in this exact format, no markdown, no explanations:\n"
        "{\n"
        '    "title": "Task title",\n'
        '    "description": "Clear task description explaining what the student needs to do",\n'
        '    "task_code": "def function_name(params):\\n    # TODO: implement this\\n    pass",\n'
        '    "language": "python"\n'
        "}\n"
        "IMPORTANT: task_code must be an EMPTY skeleton with pass and TODO comments — NOT the solution!\n"
        + reinforcement_instruction +
        "NEVER repeat a task title already mentioned in history."
    )
    prompt = (
        f"Track: {user_track.learning_track.title}\n"
        f"Student Level: {user_track.current_level}\n"
        f"Progress: {user_track.progress_score}/15\n"
        f"History:\n{history_context}\n\n"
        f"Suggest the next task."
    )

    raw_text = get_chat_completion(user, prompt, system_msg=system_msg)
    task_data = extract_json_from_text(raw_text)

    # normalize key name in case AI returns starter_code
    if "starter_code" in task_data and "task_code" not in task_data:
        task_data["task_code"] = task_data.pop("starter_code")

    validate_task_structure(task_data)
    return task_data