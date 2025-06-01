import json
from django.middleware.csrf import get_token
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
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
from rest_framework import status
import logging
import re
from rest_framework.authentication import SessionAuthentication
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
from django.views.decorators.csrf import ensure_csrf_cookie
import ollama
from ollama import chat


# 🔒 Set CSRF cookie on GET
@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def set_csrf_cookie(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrfToken": csrf_token})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    try:
        data = request.data  # Use DRF's request.data instead of json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return JsonResponse({"error": "Username and password are required"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                return JsonResponse({"error": "Account is inactive"}, status=403)
            login(request, user)
            return JsonResponse({"message": "Logged in"})
        return JsonResponse({"error": "Invalid credentials"}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email
    })


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [AllowAny]


class LearningTracksByCategory(ListAPIView):
    serializer_class = LearningTrackListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return LearningTrack.objects.filter(category_id=category_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request  # Ensure user reaches the serializer
        return context


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
        user_learning_track_id = self.request.query_params.get('user_learning_track_id')
        if user_learning_track_id:
            return UserLearningTrack.objects.filter(user=self.request.user, learning_track_pk=user_learning_track_id)
        return UserLearningTrack.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user_learning_track_id = self.request.data.get('user_learning_track_id')
        user_learning_track = get_object_or_404(LearningTrack, pk=user_learning_track_id)
        serializer.save(user=self.request.user, user_learning_track=user_learning_track)

    def perform_destroy(self, instance):
        user_learning_track_id = self.request.query_params.get('user_learning_track_id')
        user_track = get_object_or_404(UserLearningTrack, user=self.request.user, learning_track_pk=user_learning_track_id)
        user_track.delete()


class TaskDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        solution = request.data.get("solution")

        if not solution:
            return Response({"error": "Solution is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(task, data={"solution": solution}, partial=True)
        if serializer.is_valid():
            serializer.save()

            # AI grading logic
            prompt = (
                f"Task: {task.task}\n\n"
                f"User Solution: {solution}\n\n"
                "Please grade the user's solution from 0 to 5 and provide a short review."
            )

            try:
                response = chat(model="llama3", messages=[{"role": "user", "content": prompt}])
                ai_content = response.get("message", {}).get("content") or response.get("choices")[0]["message"]["content"]

                grade_match = re.search(r"\b([0-5])\b", ai_content)
                grade = int(grade_match.group(1)) if grade_match else 0

                task.grade = grade
                task.review = ai_content
                task.status = "completed" if grade == 5 else "in_progress"
                task.save()

                # ✅ Append to UserLearningTrack summary
                if task.user_learning_track:
                    progress_entry = (
                        f"Task: {task.task}\n"
                        f"Solution: {task.solution}\n"
                        f"Review: {task.review}\n"
                        f"Grade: {task.grade}/5\n"
                        "---\n"
                    )
                    user_track = task.user_learning_track
                    user_track.summary = (user_track.summary or "") + progress_entry
                    user_track.save()

            except Exception as e:
                logging.error(f"AI grading failed: {e}")
                return Response({"error": "Failed to grade solution."}, status=500)

            return Response(self.get_serializer(task).data)

        logging.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoteDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(task__user=self.request.user)


class TestAuthView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("User is:", request.user)
        return Response({"user": str(request.user)})


class GenerateNextTask(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        try:
            # Validate and retrieve the UserLearningTrack object
            user_track = get_object_or_404(UserLearningTrack, pk=user_learning_track_id, user=request.user)

            current_summary = user_track.summary or "No progress summary available."

            prompt = (
                f"User progress summary:\n{current_summary}\n\n"
                "Generate the next task for this learning track based on the user's progress."
            )

            response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])

            new_task_text = response.get('message', {}).get('content') or response.get('content')
            if not new_task_text:
                return Response({"error": "No content returned from Ollama"}, status=500)

            new_task = Task.objects.create(
                user=request.user,
                user_learning_track=user_track,
                task=new_task_text,
                status="pending"
            )

            serializer = TaskListSerializer(new_task)
            return Response(serializer.data)

        except Exception as e:
            logging.error(f"Error in GenerateNextTask: {e}")
            return Response({"error": str(e)}, status=500)