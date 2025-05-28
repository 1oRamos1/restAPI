from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .choices import DIFFICULTY_CHOICES, STATUS_CHOICES


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=100, db_index=True)

    def __str__(self):
        return self.title


class LearningTrack(models.Model):
    title = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="tracks")
    topics = models.ManyToManyField(Topic, related_name="tracks")

    users = models.ManyToManyField(User, through='UserLearningTrack', related_name='learning_tracks')

    def __str__(self):
        return self.title


class UserLearningTrack(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_learning_tracks')
    learning_track = models.ForeignKey(LearningTrack, on_delete=models.CASCADE, related_name='user_learning_tracks')
    start_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    progression = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        default=0
    )
    summary = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'learning_track')

    def __str__(self):
        return f"{self.user.username} - {self.learning_track.title}"


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks")
    user_learning_track = models.ForeignKey(UserLearningTrack, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    task = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    solution = models.TextField(blank=True)
    grade = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        blank=True,
        null=True
    )
    review = models.TextField(blank=True)
    note = models.OneToOneField('Note', on_delete=models.CASCADE, related_name="task", null=True, blank=True)

    def __str__(self):
        return self.task[:30]


class Note(models.Model):
    user_learning_track = models.ForeignKey(UserLearningTrack, on_delete=models.CASCADE, related_name="notes", null=True)
    description = models.TextField()
    creating_date = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return self.description[:50]



