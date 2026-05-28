import re
import logging
from django.db.models import Avg
from ..models import Task
from .ai_service import get_chat_completion, extract_json_from_text

logger = logging.getLogger(__name__)


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
    task_content = task.description or task.task
    prompt = (
        f"Task:\n{task_content}\n\n"
        f"Solution:\n{task.solution}\n"
        f"Review this code as a teacher. The last line must be: Grade: X/5"
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
    required = {"title", "description", "starter_code", "language"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"AI returned invalid task structure, missing fields: {missing}")


def generate_next_task_text(user, user_track) -> dict:
    history_context = get_task_history_context(user_track)

    system_msg = (
        "You are a professional coding mentor. "
        "Return ONLY a JSON object in this exact format, no markdown, no explanations:\n"
        "{\n"
        '    "title": "Task title",\n'
        '    "description": "Clear task description explaining what the student needs to do",\n'
        '    "starter_code": "def solution():\\n    pass",\n'
        '    "language": "python"\n'
        "}\n"
        "Analyze the Student Performance History. "
        "If average grades are high (4-5), increase task complexity. "
        "If grades are low (1-2), focus on review and simpler tasks. "
        "NEVER repeat a task title already mentioned in history."
    )
    prompt = (
        f"Track: {user_track.learning_track.title}\n"
        f"History:\n{history_context}\n\n"
        f"Suggest the next task."
    )

    raw_text = get_chat_completion(user, prompt, system_msg=system_msg)
    task_data = extract_json_from_text(raw_text)
    validate_task_structure(task_data)

    return task_data
