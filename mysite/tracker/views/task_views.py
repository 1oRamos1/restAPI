from django.shortcuts import get_object_or_404

from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Task, UserLearningTrack
from ..serializers import (
    TaskDetailSerializer,
    TaskListSerializer,
)
from ..services.task_service import (
    extract_student_code,
    grade_solution,
    generate_next_task_text,
    update_progress,
    get_weak_topic,
    restart_track,
    cleanup_old_tasks,
)
from ..choices import MONACO_LANGUAGES

import logging
logger = logging.getLogger(__name__)


class TaskDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer

    def get_queryset(self):
        return Task.objects.filter(user_learning_track__user=self.request.user)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        solution = request.data.get("solution", "")
        if not solution.strip():
            return Response({"error": "Solution is required."}, status=400)

        task.solution = solution
        task.save(update_fields=["solution"])

        student_code = extract_student_code(task.task_code, solution)

        if not student_code.strip():
            task.grade = 0
            task.review = "No actual implementation.\n\nGrade: 0/5"
            task.status = "completed"
            task.save()
            update_progress(task.user_learning_track, 0)
            return Response(self.get_serializer(task).data)

        try:
            result = grade_solution(request.user, task)
            task.grade = result["grade"]
            task.review = result["review"]
            task.status = "completed"
            task.save()
            # Update progress bar
            needs_reinforcement = update_progress(task.user_learning_track, result["grade"])
            if needs_reinforcement:
                # Store the weak topic on the task for later use
                task.weak_topic = task.title
                task.save(update_fields=["weak_topic"])
        except Exception:
            return Response({"error": "Failed to grade solution."}, status=500)

        return Response(self.get_serializer(task).data)


class GenerateNextTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        try:
            user_track = get_object_or_404(
                UserLearningTrack, pk=user_learning_track_id, user=request.user
            )

            last_task = Task.objects.filter(
                user_learning_track=user_track,
                status__in=["pending", "in_progress"],
            ).order_by("-id").first()

            if last_task:
                last_task.status = "completed"
                last_task.save()

            # Check if last completed task needs reinforcement
            last_completed = Task.objects.filter(
                user_learning_track=user_track,
                status="completed",
                grade__isnull=False,
            ).order_by("-id").first()

            reinforcement_topic = None
            if last_completed and last_completed.weak_topic:
                reinforcement_topic = last_completed.weak_topic

            task_data = generate_next_task_text(request.user, user_track, reinforcement_topic)

            new_task = Task.objects.create(
                user_learning_track=user_track,
                title=task_data["title"],
                description=task_data["description"],
                task_code=task_data["task_code"],
                language=task_data["language"],
                status="pending",
                is_reinforcement=bool(reinforcement_topic),
            )
            cleanup_old_tasks(user_track)
            return Response(TaskListSerializer(new_task).data)

        except Exception as e:
            logger.error(f"GenerateNextTask error: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=500)


class RestartTrack(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        user_track = get_object_or_404(
            UserLearningTrack, pk=user_learning_track_id, user=request.user
        )
        restart_track(user_track)
        return Response({"status": "restarted", "current_level": "master", "progress_score": 0})
