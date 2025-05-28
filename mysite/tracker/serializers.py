from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Topic, LearningTrack, UserLearningTrack,
    Task, Note
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title']


class LearningTrackListSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    category = CategorySerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = LearningTrack
        fields = ['id', 'title', 'level', 'level_display', 'category', 'topics']


class UserLearningTrackSerializer(serializers.ModelSerializer):
    learning_track = LearningTrackListSerializer(read_only=True)
    learning_track_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningTrack.objects.all(), source='learning_track', write_only=True
    )

    class Meta:
        model = UserLearningTrack
        fields = ['id', 'learning_track', 'learning_track_id', 'start_date', 'last_updated', 'progression', 'summary']
        read_only_fields = ['id', 'start_date', 'last_updated']

    def create(self, validated_data):
        user = self.context['request'].user
        learning_track = validated_data.pop('learning_track')
        instance, created = UserLearningTrack.objects.get_or_create(
            user=user,
            learning_track=learning_track,
            defaults=validated_data
        )
        if not created:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
        return instance


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'task', 'status', 'solution', 'grade', 'review']


class TaskDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'


class LearningTrackDetailSerializer(serializers.ModelSerializer):
    learning_track = LearningTrackListSerializer(read_only=True)
    tasks = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = UserLearningTrack
        fields = ['id', 'learning_track', 'tasks']




