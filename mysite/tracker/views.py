from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import mixins
from rest_framework.generics import (
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
import re
from .models import LearningTrack, Task, Category, UserLearningTrack, User
from .serializers import (
    LearningTrackListSerializer,
    UserLearningTrackSerializer,
    LearningTrackDetailSerializer,
    TaskDetailSerializer,
    TaskListSerializer,
    CategorySerializer
)
import logging
from django.views.decorators.csrf import ensure_csrf_cookie
import ollama
from ollama import chat


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.shortcuts import redirect
from django.contrib.auth.hashers import make_password
from .services import generate_and_save_summary


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client  # This must match what's registered in Google Cloud


def google_login_redirect(request):
    return redirect("http://localhost:8000/accounts/3rdparty/signup/")


def redirect_to_frontend(request):
    return redirect("/login")


# 🔒 Set CSRF cookie on GET
@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def set_csrf_cookie(request):
    return JsonResponse({"detail": "CSRF cookie set"})


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


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    try:
        data = request.data
        username = data.get("username")
        email = data.get("email", "").strip()
        password1 = data.get("password1")
        password2 = data.get("password2")

        if not username or not email or not password1 or not password2:
            return JsonResponse({"error": "All fields are required"}, status=400)

        if password1 != password2:
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already in use"}, status=400)

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password1)
        )

        return JsonResponse({"message": "User created successfully"}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Category.objects.all()
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)  # assumes you have a field named 'language'
        return queryset


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


class LearningTrackDetail(RetrieveAPIView):
    queryset = LearningTrack.objects.all()
    serializer_class = LearningTrackDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "trackId"

    def get_object(self):
        track_id = self.kwargs.get("trackId")
        return get_object_or_404(LearningTrack, pk=track_id)


class UserLearningTrackList(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            GenericAPIView):
    serializer_class = UserLearningTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_tracks = UserLearningTrack.objects.filter(user=user).select_related('learning_track')
        for user_track in user_tracks:
            user_track.learning_track.user_track_for_user = user_track
        return user_tracks

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        learning_track_id = request.data.get("learning_track")
        if not learning_track_id:
            return Response({"error": "Missing 'learning_track' in request body"}, status=400)

        learning_track = get_object_or_404(LearningTrack, pk=learning_track_id)
        ult, created = UserLearningTrack.objects.get_or_create(
            user=request.user,
            learning_track=learning_track
        )
        serializer = self.get_serializer(ult)
        return Response(serializer.data, status=201 if created else 200)


class UserLearningTrackDetail(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = UserLearningTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLearningTrack.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        user_learning_track_id = kwargs.get('user_learning_track_id')
        learning_track_id = kwargs.get('learning_track_id')

        if not user_learning_track_id:
            return Response({"error": "user_learning_track_id path param required"}, status=400)

        obj = get_object_or_404(self.get_queryset(), pk=user_learning_track_id, learning_track_id=learning_track_id)

        # ✅ Update progression on access
        completed_tasks = Task.objects.filter(user_learning_track=obj, status="completed").count()
        if obj.progression != completed_tasks:
            obj.progression = completed_tasks
            obj.save()

        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        user_learning_track_id = request.data.get('user_learning_track_id')
        learning_track = get_object_or_404(LearningTrack, pk=user_learning_track_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, user_learning_track=learning_track)
        return Response(serializer.data, status=201)

    def delete(self, request, *args, **kwargs):
        user_learning_track_id = kwargs.get('user_learning_track_id')
        if not user_learning_track_id:
            return Response({"error": "user_learning_track_id path param required"}, status=400)

        user_track = get_object_or_404(self.get_queryset(), pk=user_learning_track_id)
        user_track.delete()
        return Response(status=204)


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

            prompt = (
                f"Task:\n{task.task}\n\n"
                f"My Solution:\n{solution}\n\n"
                "You are a programming teacher. Review ONLY my actual solution, not the task instructions "
                "or starter code.\n"
                "If my response includes only the original function names, docstrings, or 'pass', give a 0/5.\n"
                "Ignore placeholders or boilerplate. Only consider real implementation work.\n"
                "Write ONLY the review. Be concise but helpful.\n"
                "VERY IMPORTANT:\n"
                "- Speak directly to me (second person). Start the summary with 'You..."
                "- Do NOT comment on the task text or instructions.\n"
                "- Do NOT mention the grade anywhere except the LAST LINE.\n"
                "- The last line MUST be in this exact format: Grade: <score>/5\n"
                "- If there is no actual implementation, reply with a short explanation and then: Grade: 0/5\n"
                "- Else according to the closeness to solution Grade: <0-5>/5.\n"
            )

            try:
                response = chat(model="llama3", messages=[{"role": "user", "content": prompt}])
                ai_content = response.get("message", {}).get("content") or response.get("choices")[0]["message"]["content"]

                # Extract grade
                grade_match = re.search(r"Grade[:：]?\s*(\d)\s*/\s*5\s*$", ai_content, re.IGNORECASE)
                grade = int(grade_match.group(1)) if grade_match else 0

                # Clean review body
                review_body = re.sub(r"Grade[:：]?\s*\d\s*/\s*5\s*$", "", ai_content, flags=re.IGNORECASE).strip()
                formatted_review = f"{review_body}\n\nGrade: {grade}/5"

                task.grade = grade
                task.review = formatted_review
                task.status = "inprogress"
                task.save()

                # ✅ Update progression count
                if task.user_learning_track:
                    user_track = task.user_learning_track
                    completed_tasks = Task.objects.filter(user_learning_track=user_track, status="completed").count()
                    user_track.progression = completed_tasks
                    user_track.save()

                    # ✅ Generate summary
                    all_tasks = Task.objects.filter(
                        user_learning_track=user_track,
                        status="completed"
                    ).order_by('id')

                    progress_data = "\n".join(
                        f"Title: {t.task.split('### Title:')[1].splitlines()[0].strip() if '### Title:' in t.task else 'Unknown'}\n"
                        f"Review: {t.review.strip()}"
                        for t in all_tasks if t.grade is not None
                    )

                    summary_prompt = (
                        "Please summarize my progress.\n"
                        "Here is the detailed progress so far:\n"
                        f"{progress_data}\n\n"
                        "Write a short summary (3–5 lines) that captures my overall progress, "
                        "strengths, and areas I need to improve.\n"
                        "Speak directly to me (second person). Start the summary with 'You...'.\n"
                        "Do NOT repeat individual task details. Be clear and motivating."
                        "VERY IMPORTANT:\n"
                        "- Do NOT any greetings, follow-ups or titles, just clean review.\n"
                    )

                    try:
                        summary_response = chat(model="llama3", messages=[{"role": "user", "content": summary_prompt}])
                        concise_summary = summary_response.get("message", {}).get("content") or summary_response.get("choices")[0]["message"]["content"]
                        user_track.summary = concise_summary.strip()
                        user_track.save()
                    except Exception as e:
                        logging.error(f"AI summary generation failed: {e}")

            except Exception as e:
                logging.error(f"AI grading failed: {e}")
                return Response({"error": "Failed to grade solution."}, status=500)

            return Response(self.get_serializer(task).data)

        logging.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TestAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print("User is:", request.user)
        return Response({"user": str(request.user)})


class GenerateNextTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        try:
            user_track = get_object_or_404(UserLearningTrack, pk=user_learning_track_id, user=request.user)

            last_task = Task.objects.filter(
                user=request.user,
                user_learning_track=user_track,
                status__in=["pending", "inprogress"]
            ).order_by("-id").first()

            if last_task:
                last_task.status = "completed"
                last_task.save()

                # ✅ Update progression immediately after completing a task
                completed_count = Task.objects.filter(user_learning_track=user_track, status="completed").count()
                user_track.progression = completed_count
                user_track.save()

            language_tag = user_track.learning_track.category.language  # fallback to python if not set

            prompt = (
                f"I'm a {user_track.learning_track.level} programmer student. Please act as a {user_track.learning_track.title} teacher.\n"
                f"Based on the following progress:\n{user_track.summary or 'No progress summary available.'}\n"
                "Generate the next programming task **with the exact structure below and NOTHING ELSE**:\n"
                "### Title: <A short and clear title of the task>\n"
                "### Description:\n<A short explanation of the task to complete>\n"
                f"### Code:\n```{language_tag}\n<starter code or blanks>\n```\n"
                "VERY IMPORTANT:\n"
                "- Only fill the blanks kind of tasks!.\n"
                "- Output ONLY this structure and content, task must have title , no greetings, "
                "explanations, or extra text.\n"
                "- Use the exact headings and markdown formatting as shown.\n"
                "- Include the language tag after the triple backticks exactly as shown.\n"
                "- If you cannot comply, reply only with: 'Unable to generate task.'\n"
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

            # ✅ Generate and save updated summary
            generate_and_save_summary(user_track)

            serializer = TaskListSerializer(new_task)
            return Response(serializer.data)

        except Exception as e:
            logging.error(f"Error in GenerateNextTask: {e}")
            return Response({"error": str(e)}, status=500)
