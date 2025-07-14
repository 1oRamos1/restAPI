from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Category, Topic, LearningTrack, UserLearningTrack,
    Task
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'language']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'title']


class LearningTrackListSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    category = CategorySerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    user_learning_track_id = serializers.SerializerMethodField()

    class Meta:
        model = LearningTrack
        fields = ['id', 'title', 'level', 'level_display', 'category', 'topics', 'user_learning_track_id']

    def get_user_learning_track_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            user_track = obj.user_learning_tracks.filter(user=user).first()
            return user_track.id if user_track else None
        return None


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'task', 'status', 'solution', 'grade', 'review']


class TaskDetailSerializer(serializers.ModelSerializer):
    user_learning_track_id = serializers.IntegerField(source='user_learning_track.id', read_only=True)
    task_number = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'task', 'solution', 'grade', 'review', 'status', 'user_learning_track_id', 'task_number']

    def get_task_number(self, obj):
        # get all tasks of the same user_learning_track ordered by id (or date)
        tasks = Task.objects.filter(user_learning_track=obj.user_learning_track).order_by('id')
        # find position of current task (1-based index)
        for i, t in enumerate(tasks, start=1):
            if t.id == obj.id:
                return i
        return None


class LearningTrackDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningTrack
        fields = ['id', 'title', 'level']


class UserLearningTrackSerializer(serializers.ModelSerializer):
    learning_track_id = serializers.PrimaryKeyRelatedField(
        queryset=LearningTrack.objects.all(),
        source='learning_track',
        write_only=True
    )

    # Show only `id` and `title` from the related LearningTrack
    learning_track = serializers.SerializerMethodField()
    tasks = TaskListSerializer(many=True, read_only=True)

    class Meta:
        model = UserLearningTrack
        fields = [
            'id',
            'learning_track_id',
            'learning_track',  # contains only id + title
            'start_date',
            'last_updated',
            'progression',
            'summary',
            'tasks'
        ]
        read_only_fields = ['id', 'start_date', 'last_updated', 'learning_track', 'tasks']

    def get_learning_track(self, obj):
        if obj.learning_track:
            return {
                "id": obj.learning_track.id,
                "title": obj.learning_track.title
            }
        return None

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




