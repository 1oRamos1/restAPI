from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from .models import *
from .services.ai_service import extract_json_from_text, generate_track_from_prompt
from .services.track_service import create_custom_track
from .validators import is_valid_learning_goal


class CustomUserDetailsSerializer(UserDetailsSerializer):
    is_pro = serializers.BooleanField(source='profile.is_pro', read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('is_pro',)


class CustomTrackOptionsSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["python", "js", "cpp", "auto"], default="auto")
    level = serializers.ChoiceField(choices=["beginner", "advanced", "master"])
    description = serializers.CharField(max_length=300)

    def validate_description(self, value):
        if not is_valid_learning_goal(value):
            raise serializers.ValidationError(
                "Please enter a meaningful description (3–15 words)."
            )
        return value


class CustomTrackCreateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["python", "js", "cpp", "auto"])
    description = serializers.CharField(max_length=300)
    level = serializers.ChoiceField(choices=["beginner", "advanced", "master"])

    def validate_description(self, value):
        if not is_valid_learning_goal(value):
            raise serializers.ValidationError(
                "Please enter a meaningful description (3–15 words)."
            )
        return value

    def update(self, instance, validated_data):
        raise NotImplementedError("Update not supported")

    def create(self, validated_data):
        return create_custom_track(
            user=self.context['request'].user,
            description=validated_data['description'],
            language=validated_data['language'],
            level=validated_data['level'],
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'language']


class LearningTrackListSerializer(serializers.ModelSerializer):
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    category = CategorySerializer(read_only=True)
    user_learning_track_id = serializers.SerializerMethodField()

    class Meta:
        model = LearningTrack
        fields = ['id', 'title', 'level', 'level_display', 'category', 'user_learning_track_id']

    def get_user_learning_track_id(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            user_track = obj.user_learning_tracks.filter(user=user).first()
            return user_track.id if user_track else None
        return None


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'starter_code', 'language', 'task', 'status', 'solution', 'grade', 'review']


class TaskDetailSerializer(serializers.ModelSerializer):
    user_learning_track_id = serializers.IntegerField(source='user_learning_track.id', read_only=True)
    task_number = serializers.SerializerMethodField()
    learning_track_name = serializers.CharField(source='user_learning_track.learning_track.title', read_only=True)
    learning_track_level = serializers.CharField(source='user_learning_track.learning_track.level', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'starter_code', 'language',
            'task', 'solution', 'grade', 'review', 'status',
            'user_learning_track_id', 'task_number',
            'learning_track_name', 'learning_track_level'
        ]

    def get_task_number(self, obj):
        tasks = Task.objects.filter(user_learning_track=obj.user_learning_track).order_by('id')
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
    learning_track = serializers.SerializerMethodField()
    tasks = TaskListSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = UserLearningTrack
        fields = [
            'id',
            'learning_track_id',
            'learning_track',
            'start_date',
            'category',
            'last_updated',
            'summary',
            'tasks'
        ]
        read_only_fields = ['id', 'start_date', 'last_updated', 'learning_track', 'tasks']

    def get_learning_track(self, obj):
        track = obj.learning_track
        if not track:
            return None
        return {
            "id": track.id,
            "title": track.title,
            "level": track.level,
            "category": CategorySerializer(track.category).data,
        }

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
