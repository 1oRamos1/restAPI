import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token

from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from google.oauth2 import id_token
from google.auth.transport import requests

from .serializers import *
from .ai_integration import *
from .choices import MONACO_LANGUAGES
from django.contrib.auth.models import User
from dj_rest_auth.views import PasswordResetView
from dj_rest_auth.views import UserDetailsView

from mistralai import Mistral
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY
mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)


class CustomPasswordResetView(PasswordResetView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Email not registered."}, status=status.HTTP_400_BAD_REQUEST)
        return super().post(request, *args, **kwargs)


class CustomUserDetailsView(UserDetailsView):
    serializer_class = CustomUserDetailsSerializer


def use_openai(user):
    return hasattr(user, "profile") and user.profile.is_pro


def get_chat_completion(user, prompt):
    if use_openai(user):
        response = openai.ChatCompletion.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message["content"]
    else:
        try:
            chat_response = mistral_client.chat.complete(
                model="ministral-3b-latest",  # latest Mistral chat model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            logging.error(f"Mistral API call failed: {e}")
            return "Error: AI response unavailable."


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_to_pro(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.is_pro = True
    profile.save()
    return Response({'status': 'upgraded to pro'})


logger = logging.getLogger(__name__)
@ method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print("GoogleLoginView called")
        print(f"Request data: {request.data}")
        print(f"Request headers: {dict(request.headers)}")
        print(f"Content type: {request.content_type}")
        try:
            # Get the credential from request
            credential = request.data.get('credential') or request.data.get('id_token') or request.data.get(
                'access_token')

            if not credential:
                return Response({'error': 'No credential provided'}, status=400)

            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                credential,
                requests.Request(),
                settings.SOCIAL_AUTH_GOOGLE_CLIENT_ID)

            # Extract user info
            email = idinfo['email']
            name = idinfo['name']

            # Get or create user
            first_name = name.split()[0] if name else ''
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email, 'first_name': first_name}
            )

            # Log the user in (or return token)
            login(request, user)

            return Response({'success': True, 'user': user.username})

        except Exception as e:
            logger.error(f"Google login error: {str(e)}")
            return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def set_csrf_cookie(request):
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    user = authenticate(request, username=data.get("username"), password=data.get("password"))
    if user:
        login(request, user)
        return JsonResponse({"message": "Logged in"})
    return JsonResponse({"error": "Invalid credentials"}, status=403)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response({"message": "Logged out successfully"}, status=200)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
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
    login(request, user)
    return JsonResponse({"message": "User created successfully"}, status=201)


class CustomTrackOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CustomTrackOptionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        lang_input = data['language']
        lang_prompt = (
            lang_input if lang_input != 'auto'
            else f"one of the following: {', '.join(MONACO_LANGUAGES)}"
        )

        prompt = f"""
           User wants a {data['level']} programming learning track.
           Language preference: {lang_prompt}.
           Learning goal: {data['description']}
           Suggest 3 to 5 learning tracks as a JSON ARRAY ONLY with this format:
           [
               {{
                   "title": "Track title",
                   "language": "Programming language",
                   "level": "beginner|advanced|master",
                   "short_description": "A short summary of the learning track"
               }},
               ...
           ]
           Do NOT include any other text, explanations, or formatting.
           Return ONLY valid JSON.
           """

        ai_response_text = generate_track_from_prompt(prompt)
        try:
            options = extract_json_from_text(ai_response_text)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=400)

        if not isinstance(options, list) or not options:
            return Response({"detail": "AI did not return a valid list of options."}, status=400)

        return Response({"options": options})


class CustomTrackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not getattr(request.user.profile, 'is_pro', False):
            return Response({'detail': 'Pro membership required.'}, status=403)

        serializer = CustomTrackCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user_learning_track = serializer.save()

        return Response({
            'track_id': user_learning_track.learning_track.id,
            'user_track_id': user_learning_track.id
        }, status=status.HTTP_201_CREATED)


class CategoryList(ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Category.objects.all()
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        return queryset


class LearningTracksByCategory(ListAPIView):
    serializer_class = LearningTrackListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return LearningTrack.objects.filter(category_id=self.kwargs['category_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LearningTrackDetail(RetrieveAPIView):
    queryset = LearningTrack.objects.all()
    serializer_class = LearningTrackDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "trackId"

    def get_object(self):
        return get_object_or_404(LearningTrack, pk=self.kwargs.get("trackId"))


class UserLearningTrackList(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            GenericAPIView):
    serializer_class = UserLearningTrackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_tracks = UserLearningTrack.objects.filter(user=self.request.user).select_related('learning_track')
        for user_track in user_tracks:
            user_track.learning_track.user_track_for_user = user_track
        return user_tracks

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        learning_track = get_object_or_404(LearningTrack, pk=request.data.get("learning_track"))
        ult, created = UserLearningTrack.objects.get_or_create(user=request.user, learning_track=learning_track)
        serializer = self.get_serializer(ult)
        return Response(serializer.data, status=201 if created else 200)

    def delete(self, request, *args, **kwargs):
        # Get track id from body or query params
        ult_id = request.data.get("user_learning_track_id") or request.query_params.get("user_learning_track_id")
        if not ult_id:
            return Response({"error": "user_learning_track_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        user_track = get_object_or_404(UserLearningTrack, pk=ult_id, user=request.user)
        user_track.delete()
        return Response({"detail": "Track deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


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
        obj = get_object_or_404(
            self.get_queryset(),
            pk=kwargs.get('user_learning_track_id'),
            learning_track_id=kwargs.get('learning_track_id')
        )
        completed = Task.objects.filter(user_learning_track=obj, status="completed").count()
        if obj.progression != completed:
            obj.progression = completed
            obj.save()
        return Response(self.get_serializer(obj).data)

    def post(self, request, *args, **kwargs):
        learning_track_id = request.data.get('learning_track_id')
        if not learning_track_id:
            return Response({"error": "Missing learning_track_id"}, status=400)
        track = get_object_or_404(LearningTrack, pk=learning_track_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, learning_track=track)
        return Response(serializer.data, status=201)

    def delete(self, request, *args, **kwargs):
        user_track = get_object_or_404(self.get_queryset(), pk=kwargs.get('user_learning_track_id'))
        user_track.delete()
        return Response(status=204)


class TaskDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def extract_student_code(self, task_text, student_solution):
        """
        Extracts only the student's actual code, ignoring AI instructions and placeholders.
        """
        task_lines = set(task_text.splitlines())
        student_lines = [
            line for line in student_solution.splitlines()
            if line.strip() and line not in task_lines and not re.match(r'(pass|# TODO|___+)', line.strip())
        ]
        return "\n".join(student_lines)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        solution = request.data.get("solution", "")

        if not solution.strip():
            return Response({"error": "Solution is required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(task, data={"solution": solution}, partial=True)
        if serializer.is_valid():
            serializer.save()

            student_code = self.extract_student_code(task.task, solution)

            # Assign grade 0 if no student code
            if not student_code.strip():
                task.grade = 0
                task.review = "No actual implementation.\n\nGrade: 0/5"
                task.status = "inprogress"
                task.save()
                return Response(self.get_serializer(task).data)

            # Prepare AI review prompt
            prompt = (
                f"Task:\n{task.task}\n\n"
                f"My Solution:\n{solution}\n\n"
                "You are a programming teacher. Review ONLY my actual solution, not the task instructions "
                "or starter code ('# TODO').\n"
                "Follow these rules strictly:\n"
                "- Do NOT provide the full solution. Only give hints or guidance.\n"
                "- Ignore any boilerplate code or placeholders.\n"
                "- Speak directly to the student (second person). Start the review with 'You...'\n"
                "- The LAST line MUST be: Grade: <score>/5\n"
                "- Only the last line contains the grade. No other grades mentioned.\n"
                "- If no actual implementation, reply with 'Grade: 0/5'.\n"
                "- Otherwise, assign a grade from 1-5 based on correctness and closeness to solution.\n"
                "- Do NOT include example usage, solutions, or explanations outside hints.\n"
                "STRICTLY follow this format."
            )

            try:
                ai_content = get_chat_completion(request.user, prompt)

                grade_match = re.search(r"Grade[:：]?\s*(\d)\s*/\s*5\s*$", ai_content, re.IGNORECASE)
                grade = int(grade_match.group(1)) if grade_match else 0

                review_body = re.sub(r"Grade[:：]?\s*\d\s*/\s*5\s*$", "", ai_content, flags=re.IGNORECASE).strip()
                formatted_review = f"{review_body}\n\nGrade: {grade}/5"

                task.grade = grade
                task.review = formatted_review
                task.status = "inprogress"
                task.save()

            except Exception as e:
                logging.error(f"AI grading failed: {e}")
                return Response({"error": "Failed to grade solution."}, status=500)

            return Response(self.get_serializer(task).data)

        logging.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenerateNextTask(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_learning_track_id):
        try:
            user_track = get_object_or_404(UserLearningTrack, pk=user_learning_track_id, user=request.user)

            # Complete the last pending/inprogress task
            last_task = Task.objects.filter(
                user=request.user,
                user_learning_track=user_track,
                status__in=["pending", "inprogress"]
            ).order_by("-id").first()

            if last_task:
                last_task.status = "completed"
                last_task.save()

            # Build AI prompt with next difficulty
            prompt = (
                f"I'm a {user_track.learning_track.level} programmer student. "
                f"Please act as a {user_track.learning_track.title} teacher.\n"
                f"Based on the following progress:\n{user_track.summary or 'No progress summary available.'}\n"
                "**with the exact structure below and NOTHING ELSE**:\n"
                "### Title: <A short and clear title of the task>\n"
                "### Description:\n<A short explanation of the task to complete>\n"
                f"### Code:\n```{user_track.learning_track.category.language}\n<starter code with FILL-IN-THE-BLANK lines, marked as underscores or # TODOs and blank spaces>\n```\n"
                "VERY IMPORTANT:\n"
                "- Do NOT provide the solution!\n"
                "- Insert several blanks where the student must write code.\n"
                "- Do not include example usage or final printouts.\n"
                "- Only output in the requested markdown format, no extra explanations.\n"
            )

            result_text = get_chat_completion(request.user, prompt)

            if not result_text:
                return Response({"error": "No content returned"}, status=500)

            new_task = Task.objects.create(
                user=request.user,
                user_learning_track=user_track,
                task=result_text,
                status="pending",
            )

            return Response(TaskListSerializer(new_task).data)

        except Exception as e:
            logging.error(f"GenerateNextTask failed: {e}")
            return Response({"error": str(e)}, status=500)


