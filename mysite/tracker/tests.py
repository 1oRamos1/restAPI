from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from .models import Profile, Category, LearningTrack, UserLearningTrack, Task

BASE = '/api/v1/tracker'


def create_user(username="testuser", password="testpass123", is_pro=False):
    user = User.objects.create_user(username=username, password=password, email=f"{username}@test.com")
    Profile.objects.get_or_create(user=user, defaults={"is_pro": is_pro})
    return user


def create_track(user, title="Test Track", level="beginner", language="python"):
    category = Category.objects.create(name="Test Category", language=language)
    track = LearningTrack.objects.create(title=title, category=category, level=level)
    return UserLearningTrack.objects.create(user=user, learning_track=track)


# ==========================================
# 1. Auth Tests
# ==========================================

class SignupTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_signup_success(self):
        res = self.client.post(f'{BASE}/auth/signup/', {
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_signup_passwords_dont_match(self):
        res = self.client.post(f'{BASE}/auth/signup/', {
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "strongpass123",
            "password2": "wrongpass",
        })
        self.assertEqual(res.status_code, 400)

    def test_signup_duplicate_username(self):
        create_user(username="existing")
        res = self.client.post(f'{BASE}/auth/signup/', {
            "username": "existing",
            "email": "other@test.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        })
        self.assertEqual(res.status_code, 400)

    def test_signup_missing_fields(self):
        res = self.client.post(f'{BASE}/auth/signup/', {"username": "newuser"})
        self.assertEqual(res.status_code, 400)


class LoginTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_login_success(self):
        res = self.client.post(f'{BASE}/auth/login/', {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertEqual(res.status_code, 200)

    def test_login_wrong_password(self):
        res = self.client.post(f'{BASE}/auth/login/', {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(res.status_code, 403)

    def test_logout(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(f'{BASE}/auth/logout/')
        self.assertEqual(res.status_code, 200)


# ==========================================
# 2. Learning Track Tests
# ==========================================

class UserTrackTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_user_tracks_empty(self):
        res = self.client.get(f'{BASE}/user/tracks/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_add_track(self):
        category = Category.objects.create(name="Web", language="js")
        track = LearningTrack.objects.create(title="React Basics", category=category, level="beginner")
        res = self.client.post(f'{BASE}/user/tracks/', {"learning_track": track.id})
        self.assertEqual(res.status_code, 201)

    def test_add_same_track_twice_returns_200(self):
        category = Category.objects.create(name="Web", language="js")
        track = LearningTrack.objects.create(title="React Basics", category=category, level="beginner")
        self.client.post(f'{BASE}/user/tracks/', {"learning_track": track.id})
        res = self.client.post(f'{BASE}/user/tracks/', {"learning_track": track.id})
        self.assertEqual(res.status_code, 200)

    def test_delete_track(self):
        user_track = create_track(self.user)
        res = self.client.delete(f'{BASE}/user/tracks/', {"user_learning_track_id": user_track.id})
        self.assertEqual(res.status_code, 204)
        self.assertFalse(UserLearningTrack.objects.filter(pk=user_track.id).exists())

    def test_delete_track_of_other_user_fails(self):
        other_user = create_user(username="other")
        other_track = create_track(other_user)
        res = self.client.delete(f'{BASE}/user/tracks/', {"user_learning_track_id": other_track.id})
        self.assertEqual(res.status_code, 404)


# ==========================================
# 3. Task Tests
# ==========================================

class TaskTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.user_track = create_track(self.user)
        self.task = Task.objects.create(
            user_learning_track=self.user_track,
            title="Learn Loops",
            description="Write a function that sums a list.",
            starter_code="def sum_list(lst):\n    pass",
            language="python",
            status="pending",
        )

    def test_get_task(self):
        res = self.client.get(f'{BASE}/user/tasks/{self.task.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['title'], "Learn Loops")

    def test_get_task_of_other_user_fails(self):
        other_user = create_user(username="other")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        res = other_client.get(f'{BASE}/user/tasks/{self.task.id}/')
        self.assertEqual(res.status_code, 404)

    def test_submit_empty_solution_fails(self):
        res = self.client.put(f'{BASE}/user/tasks/{self.task.id}/', {"solution": ""})
        self.assertEqual(res.status_code, 400)

    @patch('tracker.services.task_service.get_chat_completion')
    def test_submit_solution_grades_task(self, mock_ai):
        mock_ai.return_value = "Good solution!\n\nGrade: 4/5"
        res = self.client.put(f'{BASE}/user/tasks/{self.task.id}/', {
            "solution": "def sum_list(lst):\n    return sum(lst)"
        })
        self.assertEqual(res.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.grade, 4)
        self.assertEqual(self.task.status, "in_progress")

    @patch('tracker.services.task_service.get_chat_completion')
    def test_submit_no_real_code_gives_zero(self, mock_ai):
        mock_ai.return_value = "No implementation.\n\nGrade: 0/5"
        res = self.client.put(f'{BASE}/user/tasks/{self.task.id}/', {
            "solution": "def sum_list(lst):\n    pass"
        })
        self.assertEqual(res.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.grade, 0)


# ==========================================
# 4. Generate Next Task Tests
# ==========================================

class GenerateNextTaskTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.user_track = create_track(self.user)

    @patch('tracker.services.task_service.get_chat_completion')
    def test_generate_task_creates_new_task(self, mock_ai):
        mock_ai.return_value = '{"title": "New Task", "description": "Do this", "starter_code": "pass", "language": "python"}'
        res = self.client.post(f'{BASE}/user/tracks/{self.user_track.id}/generate-task/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Task.objects.filter(user_learning_track=self.user_track).count(), 1)

    @patch('tracker.services.task_service.get_chat_completion')
    def test_generate_task_completes_previous_task(self, mock_ai):
        mock_ai.return_value = '{"title": "New Task", "description": "Do this", "starter_code": "pass", "language": "python"}'
        Task.objects.create(
            user_learning_track=self.user_track,
            title="Old Task",
            status="pending",
        )
        self.client.post(f'{BASE}/user/tracks/{self.user_track.id}/generate-task/')
        old_task = Task.objects.get(title="Old Task")
        self.assertEqual(old_task.status, "completed")


# ==========================================
# 5. Summary Tests
# ==========================================

class SummaryTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)
        self.user_track = create_track(self.user)

    @patch('tracker.services.track_service.mistral_client')
    def test_generate_summary_with_completed_tasks(self, mock_mistral):
        Task.objects.create(
            user_learning_track=self.user_track,
            title="Task 1",
            status="completed",
            grade=4,
            review="Good job!",
        )
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "You have done well!"
        mock_mistral.chat.complete.return_value = mock_response

        res = self.client.post(f'{BASE}/user/tracks/{self.user_track.id}/summary/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['summary'], "You have done well!")

    def test_generate_summary_no_tasks(self):
        res = self.client.post(f'{BASE}/user/tracks/{self.user_track.id}/summary/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['summary'], "No progress yet.")

    def test_generate_summary_other_user_fails(self):
        other_user = create_user(username="other")
        other_client = APIClient()
        other_client.force_authenticate(user=other_user)
        res = other_client.post(f'{BASE}/user/tracks/{self.user_track.id}/summary/')
        self.assertEqual(res.status_code, 404)