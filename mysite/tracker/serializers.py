from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from .models import *
from .ai_integration import generate_track_from_prompt, extract_json_from_text


class CustomUserDetailsSerializer(UserDetailsSerializer):
    is_pro = serializers.BooleanField(source='profile.is_pro', read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('is_pro',)


class CustomTrackOptionsSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["python", "js", "cpp", "auto"], default="auto")
    level = serializers.ChoiceField(choices=["beginner", "advanced", "master"])
    description = serializers.CharField(max_length=300)


class CustomTrackCreateSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=["python", "js", "cpp", "auto"])
    description = serializers.CharField(max_length=300)
    level = serializers.ChoiceField(choices=["beginner", "advanced", "master"])

    def update(self, instance, validated_data):
        raise NotImplementedError("Update not supported")

    def validate_description(self, value):
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        prompt = validated_data['description']
        selected_lang = validated_data['language']
        selected_level = validated_data['level']

        if selected_lang != "auto":
            full_prompt = f"Create a {selected_level} track in {selected_lang} about: {prompt}"
        else:
            full_prompt = f"Create a {selected_level} track based on: {prompt}. Choose the most suitable language."

        ai_response_text = generate_track_from_prompt(full_prompt)
        track_data = extract_json_from_text(ai_response_text)

        category_name = track_data.get('category')
        language = track_data.get('language') or (selected_lang if selected_lang != 'auto' else 'python')

        category, _ = Category.objects.get_or_create(name=category_name.strip(), language=language)

        learning_track = LearningTrack.objects.create(
            title=track_data['title'],
            category=category,
            level=track_data['level'],
            is_custom=True,
            created_by=user
        )

        user_learning_track = UserLearningTrack.objects.create(
            user=user,
            learning_track=learning_track
        )

        return user_learning_track


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
    learning_track_name = serializers.CharField(source='user_learning_track.learning_track.title', read_only=True)
    learning_track_level = serializers.CharField(source='user_learning_track.learning_track.level', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'task', 'solution', 'grade', 'review', 'status', 'user_learning_track_id', 'task_number', 'learning_track_name', 'learning_track_level']

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
            'progression',
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



