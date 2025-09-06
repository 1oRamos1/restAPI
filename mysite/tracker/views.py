import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dj_rest_auth.views import UserDetailsView
from google.oauth2 import id_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token
from google.auth.transport import requests
import ollama

from .serializers import *
from .ai_integration import *
from .validators import is_valid_learning_goal, is_valid_track_structure
from .choices import MONACO_LANGUAGES
from django.contrib.auth.models import User
from dj_rest_auth.views import PasswordResetView
from rest_framework.response import Response
from rest_framework import status

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
                model="mistral-large-latest",  # latest Mistral chat model
                messages=[{"role": "user", "content": prompt}],
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
                "- Speak directly to me (second person). Start the summary with 'You...'\n"
                "- Do NOT comment on the task text or instructions.\n"
                "- Do NOT mention the grade anywhere except the LAST LINE.\n"
                "- The last line MUST be in this exact format: Grade: <score>/5\n"
                "- If there is no actual implementation, reply with a short explanation and then: Grade: 0/5\n"
                "- Else according to the closeness to solution Grade: <0-5>/5.\n"
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

                if task.user_learning_track:
                    user_track = task.user_learning_track
                    completed_tasks = Task.objects.filter(user_learning_track=user_track, status="completed").count()
                    user_track.progression = completed_tasks
                    user_track.save()

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
                        "Do NOT repeat individual task details. Be clear and motivating.\n"
                        "VERY IMPORTANT:\n"
                        "- Do NOT include greetings, follow-ups or titles, just clean review.\n"
                    )

                    try:
                        concise_summary = get_chat_completion(request.user, summary_prompt)
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

                user_track.progression = Task.objects.filter(user_learning_track=user_track, status="completed").count()
                user_track.save()

            prompt = (
                f"I'm a {user_track.learning_track.level} programmer student. Please act as a {user_track.learning_track.title} teacher.\n"
                f"Based on the following progress:\n{user_track.summary or 'No progress summary available.'}\n"
                "Generate the next programming task **with the exact structure below and NOTHING ELSE**:\n"
                "### Title: <A short and clear title of the task>\n"
                "### Description:\n<A short explanation of the task to complete>\n"
                f"### Code:\n```{user_track.learning_track.category.language}\n<starter code or blanks>\n```\n"
                "VERY IMPORTANT:\n"
                "- Only fill the blanks kind of tasks!\n"
                "- Use the exact markdown format shown.\n"
                "- No greetings, no explanations, only valid content.\n"
            )

            result_text = get_chat_completion(request.user, prompt)

            if not result_text:
                return Response({"error": "No content returned"}, status=500)

            new_task = Task.objects.create(
                user=request.user,
                user_learning_track=user_track,
                task=result_text,
                status="pending"
            )

            # Optional: regenerate summary if needed here

            return Response(TaskListSerializer(new_task).data)

        except Exception as e:
            logging.error(f"GenerateNextTask failed: {e}")
            return Response({"error": str(e)}, status=500)


class FreeformCustomTrackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = getattr(user, "profile", None)
        if not profile or not profile.is_pro:
            return Response({'detail': 'Pro membership required.'}, status=status.HTTP_403_FORBIDDEN)

        learning_goal = request.data.get('learning_goal', '').strip()
        if not learning_goal:
            return Response({'detail': 'Missing learning goal.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate input meaning
        if not is_valid_learning_goal(learning_goal):
            return Response({'detail': 'Invalid or meaningless learning goal.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Generate AI track JSON string
            ai_response = generate_track_from_prompt(learning_goal)
            # Parse AI JSON output
            track_data = json.loads(ai_response)
        except (ValidationError, json.JSONDecodeError) as e:
            return Response({'detail': f'AI generation failed or invalid output: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate AI structured output format
        if not is_valid_track_structure(track_data):
            return Response({'detail': 'AI output invalid structure.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract required fields
        language = track_data.get('language')
        category_name = track_data.get('category')
        level = track_data.get('level')
        title = track_data.get('title', learning_goal)  # fallback

        # Find or create Category by name & language
        category = Category.objects.filter(name__iexact=category_name, language=language).first()
        if not category:
            return Response({'detail': f'Category "{category_name}" with language "{language}" not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create LearningTrack
        learning_track = LearningTrack.objects.create(
            title=title,
            category=category,
            level=level,
            is_custom=True  # flag for DIY track
        )

        # Create Tasks from AI data
        for task_data in track_data['tasks']:
            learning_track.tasks.create(
                title=task_data['title'],
                description=task_data['description'],
                difficulty=task_data.get('difficulty', 'medium'),
            )

        # Create UserLearningTrack
        user_learning_track = UserLearningTrack.objects.create(
            user=user,
            learning_track=learning_track,
            progression=0,
            summary='',
        )

        return Response({
            'learning_track_id': learning_track.id,
            'user_learning_track_id': user_learning_track.id,
            'redirect_url': f'/track/{learning_track.id}/{user_learning_track.id}'
        }, status=status.HTTP_201_CREATED)



