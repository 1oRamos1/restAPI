from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    CreateAPIView,
    DestroyAPIView
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import LearningTrack, Task, Note, Category, UserLearningTrack
from .serializers import (
    LearningTrackListSerializer,
    LearningTrackDetailSerializer,
    UserLearningTrackSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    NoteSerializer,
    CategorySerializer
)
import logging

import ollama


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [AllowAny]


class LearningTracksByCategory(ListAPIView):
    serializer_class = LearningTrackListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        tracks = LearningTrack.objects.filter(category_id=category_id)

        user = self.request.user
        if user.is_authenticated:
            for track in tracks:
                track.user_track_for_user = UserLearningTrack.objects.filter(
                    user=user, learning_track=track
                ).first()
        else:
            for track in tracks:
                track.user_track_for_user = None

        return tracks


class UserLearningTrackList(ListAPIView):
    serializer_class = UserLearningTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_tracks = UserLearningTrack.objects.filter(user=user).select_related('learning_track')
        # Attach user_track_for_user to learning_track for nested serializer
        for user_track in user_tracks:
            user_track.learning_track.user_track_for_user = user_track
        return user_tracks


class UserLearningTrackCreateDelete(CreateAPIView, DestroyAPIView):
    serializer_class = UserLearningTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLearningTrack.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class LearningTrackDetail(RetrieveAPIView):
    serializer_class = LearningTrackDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(
            UserLearningTrack,
            user=self.request.user,
            pk=self.kwargs['pk']
        )


class TaskDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        task = self.get_object()
        solution = self.request.data.get("solution")
        if solution:
            serializer.save(solution=solution)

            # AI grading example, adjust or remove if you don't have AI setup
            prompt = (
                f"Task: {task.task}\n\n"
                f"User Solution: {solution}\n\n"
                "Please grade the user's solution from 0 to 5 and provide a short review."
            )
            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
            ai_content = response.get("choices")[0].get("message").get("content")

            import re
            grade_match = re.search(r"([0-5])", ai_content)
            grade = int(grade_match.group(1)) if grade_match else 0

            task.grade = grade
            task.review = ai_content
            task.status = "completed" if grade == 5 else "in_progress"
            task.save()


class NoteDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(task__user=self.request.user)


class TestAuthView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("User is:", request.user)
        return Response({"user": str(request.user)})


class GenerateNextTask(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, track_id):
        print("zubiiiii")
        try:
            # Get the UserLearningTrack by pk only, ignore user for now
            user_track = get_object_or_404(UserLearningTrack, pk=track_id)

            current_summary = user_track.summary or "No progress summary available."

            prompt = (
                f"User progress summary:\n{current_summary}\n\n"
                "Generate the next task for this learning track based on the user's progress."
            )

            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])

            # Extract response content safely
            new_task_text = None
            if isinstance(response, dict):
                new_task_text = response.get('message', {}).get('content') or response.get('content')
            elif hasattr(response, 'message'):
                new_task_text = response.message.content
            else:
                new_task_text = str(response)

            if not new_task_text:
                return Response({"error": "No content returned from Ollama"}, status=500)

            new_task = Task.objects.create(
                user=request.user,  # no user for testing
                user_learning_track=user_track,
                task=new_task_text,
                status="pending"
            )

            serializer = TaskListSerializer(new_task)
            return Response(serializer.data)

        except Exception as e:
            logging.error(f"Error in GenerateNextTask: {e}")
            return Response({"error": str(e)}, status=500)