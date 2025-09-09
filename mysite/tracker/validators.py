import re

ALLOWED_CHARS_PATTERN = re.compile(
    r'^[\w\s.,!?\'"()\-\+:;<>[\]{}@#%^&*/\\=~`|]{10,300}$',
    re.UNICODE
)

BANNED_WORDS = {
    "asdf", "qwerty", "blah", "123456", "gibberish", "test", "lorem",
    "fuck", "shit", "idiot", "dumb"
}


def is_valid_learning_goal(goal: str) -> bool:
    """
    Validates a learning goal string:
    - Length: 10–300 characters
    - Word count: 3–15
    - Allowed characters only
    - No banned words
    - Not just repeated characters
    - Not too short of character variety
    """
    if not isinstance(goal, str):
        return False

    cleaned = goal.strip().lower()

    if not (10 <= len(cleaned) <= 300):
        return False

    words = cleaned.split()
    if not (3 <= len(words) <= 15):
        return False

    if not ALLOWED_CHARS_PATTERN.match(cleaned):
        return False

    if any(banned in cleaned for banned in BANNED_WORDS):
        return False

    # Prevent inputs like "aaaaaaa" or "1111111111"
    if len(set(cleaned)) < 5:
        return False

    return True


def is_valid_track_structure(data: dict) -> bool:
    """
    Validates the AI response for a custom track:
    - Includes required fields
    - 'tasks' is a list of 1-20 items
    - Each task is a dict with 'title' and 'description'
    - Description length is reasonable
    """
    if not isinstance(data, dict):
        return False

    required_fields = {"title", "language", "category", "level", "tasks"}
    if not required_fields.issubset(data):
        return False

    tasks = data.get("tasks")
    if not isinstance(tasks, list) or not (1 <= len(tasks) <= 20):
        return False

    for task in tasks:
        if not isinstance(task, dict):
            return False
        if "title" not in task or "description" not in task:
            return False
        if not (10 <= len(task["description"]) <= 1000):
            return False

    return True
