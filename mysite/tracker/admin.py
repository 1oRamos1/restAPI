from django.contrib import admin
from .models import Category, Topic, LearningTrack, UserLearningTrack, Task, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(LearningTrack)
class LearningTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'level', 'category')
    list_filter = ('level', 'category')
    search_fields = ('title',)
    filter_horizontal = ('topics',)  # nice UI for ManyToMany topics


@admin.register(UserLearningTrack)
class UserLearningTrackAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'learning_track', 'start_date', 'progression', 'last_updated')
    search_fields = ('user__username', 'learning_track__title')
    list_filter = ('start_date',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_learning_track', 'status', 'grade')
    search_fields = ('task', 'user__username', 'user_learning_track__title')
    list_filter = ('status', 'grade')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_learning_track', 'description', 'creating_date')
    search_fields = ('description',)
    list_filter = ('creating_date',)

