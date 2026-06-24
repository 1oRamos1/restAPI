from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .choices import DIFFICULTY_CHOICES, STATUS_CHOICES, LEVEL_CHOICES


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_pro = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    language = models.CharField(max_length=20, default='python')

    def __str__(self):
        return self.name


class LearningTrack(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tracks")
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="custom_tracks")
    title = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    is_custom = models.BooleanField(default=False)

    users = models.ManyToManyField(User, through='UserLearningTrack', related_name='learning_tracks')

    def __str__(self):
        return self.title


class UserLearningTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_learning_tracks')
    learning_track = models.ForeignKey(LearningTrack, on_delete=models.CASCADE, related_name='user_learning_tracks')

    summary = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    current_level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='explorer')
    progress_score = models.IntegerField(default=0)  # counts successful tasks toward 15

    class Meta:
        unique_together = ('user', 'learning_track')

    def __str__(self):
        return f"{self.user.username} - {self.learning_track.title}"


class Task(models.Model):
    user_learning_track = models.ForeignKey(UserLearningTrack, on_delete=models.CASCADE, related_name="tasks")

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    task_code = models.TextField(blank=True)
    language = models.CharField(max_length=30, blank=True)
    solution = models.TextField(blank=True)
    review = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    grade = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    is_reinforcement = models.BooleanField(default=False)  # True if generated as reinforcement task
    weak_topic = models.CharField(max_length=200, blank=True)  # topic this reinforcement targets

    def __str__(self):
        return self.title[:30] if self.title else 'Untitled Task'
