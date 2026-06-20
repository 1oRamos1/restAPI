from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(LearningTrack)
class LearningTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'category')
    list_filter = ('level', 'category')
    search_fields = ('title',)


@admin.register(UserLearningTrack)
class UserLearningTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'learning_track', 'current_level', 'progress_score', 'start_date', 'last_updated')
    search_fields = ('user__username', 'learning_track__title')
    list_filter = ('start_date', 'current_level')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user_learning_track', 'status', 'grade', 'is_reinforcement')
    search_fields = ('title', 'user_learning_track__user__username', 'user_learning_track__learning_track__title')
    list_filter = ('status', 'grade', 'is_reinforcement')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_pro')
    search_fields = ('user__username',)
    list_filter = ('is_pro',)
