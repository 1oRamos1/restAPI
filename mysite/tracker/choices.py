DIFFICULTY_CHOICES = (
    ('beginner', 'Beginner'),
    ('advanced', 'Advanced'),
    ('master', 'Master'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
)

LEVEL_CHOICES = (
    ('explorer', 'Explorer'),
    ('builder', 'Builder'),
    ('master', 'Master'),
)

MONACO_LANGUAGES = [
    "python", "javascript", "typescript", "html", "css", "json", "markdown",
    "cpp", "c", "java", "go", "shell", "bash", "php", "sql", "xml", "yaml", "rust"
]

# Progress thresholds per position in the 15-task cycle
# positions 0-4: need >= 2, positions 5-9: need >= 3, positions 10-14: need >= 4
def get_required_grade(progress_score: int, current_level: str = 'explorer') -> int:
    if current_level == 'master':
        return 4
    pos = progress_score % 15
    if pos < 5:
        return 2
    elif pos < 10:
        return 3
    else:
        return 4
