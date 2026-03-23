from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from async_tasks.models import AsyncTaskExecution, TaskStatus


class PlatformSmokeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass123456", role=UserRole.TEST)

    def test_dashboard_is_reachable(self):
        response = Client().get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_async_task_callback_updates_status_and_sends_notification(self):
        task = AsyncTaskExecution.objects.create(title="demo", callback_token="token-1", created_by=self.user)
        response = Client().post(
            reverse("async_tasks:task-callback", kwargs={"token": "token-1"}),
            data='{"status": "SUCCESS", "result": "ok"}',
            content_type="application/json",
        )
        task.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.status, TaskStatus.SUCCESS)
        self.assertEqual(self.user.notifications.count(), 1)

    def test_login_and_profile_pages(self):
        client = Client()
        login_response = client.post(reverse("accounts:login"), {"username": "tester", "password": "pass123456"})
        self.assertEqual(login_response.status_code, 302)
        profile_response = client.get(reverse("accounts:profile"))
        self.assertEqual(profile_response.status_code, 200)
