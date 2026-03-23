from unittest.mock import MagicMock, patch

from django.test import Client, TestCase
from django.urls import reverse
from django.test.utils import override_settings

from projects.models import Project

from .models import CIIntegration, CIProvider, TaskStatus, TaskType, AsyncTaskExecution
from .services import CITriggerService


class CITriggerServiceTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Demo", code="DEMO-CI")

    @patch("async_tasks.services.request.urlopen")
    def test_trigger_jenkins(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b"queued"
        response.headers = {"Location": "https://jenkins.example/queue/1"}
        response.__enter__.return_value = response
        mock_urlopen.return_value = response

        integration = CIIntegration.objects.create(
            project=self.project,
            name="jenkins",
            provider=CIProvider.JENKINS,
            base_url="https://jenkins.example",
            callback_base_url="https://platform.example",
            jenkins_job_name="demo-job",
        )
        task = AsyncTaskExecution.objects.create(project=self.project, integration=integration, task_type=TaskType.SUITE_RUN, title="demo")
        result = CITriggerService(integration).trigger(task)
        task.refresh_from_db()

        self.assertEqual(task.status, TaskStatus.RUNNING)
        self.assertEqual(task.source, "JENKINS")
        self.assertIn("queue_url", result)

    @patch("async_tasks.services.request.urlopen")
    def test_trigger_gitlab(self, mock_urlopen):
        response = MagicMock()
        response.read.return_value = b'{"id": 12, "ref": "main"}'
        response.__enter__.return_value = response
        mock_urlopen.return_value = response

        integration = CIIntegration.objects.create(
            project=self.project,
            name="gitlab",
            provider=CIProvider.GITLAB_CI,
            base_url="https://gitlab.example",
            callback_base_url="https://platform.example",
            gitlab_project_id="123",
            gitlab_trigger_token="token",
        )
        task = AsyncTaskExecution.objects.create(project=self.project, integration=integration, task_type=TaskType.SUITE_RUN, title="demo")
        result = CITriggerService(integration).trigger(task)
        task.refresh_from_db()

        self.assertEqual(task.status, TaskStatus.RUNNING)
        self.assertEqual(task.external_build_id, "12")
        self.assertEqual(result["id"], 12)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TaskActionViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(name="Demo", code="DEMO-ACTION")

    def test_start_pending_task_from_ui(self):
        task = AsyncTaskExecution.objects.create(project=self.project, title="manual-run", status=TaskStatus.PENDING)
        response = self.client.post(reverse("async_tasks:task-action", kwargs={"task_id": task.id}), {"action": "start"})
        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(task.status, TaskStatus.SUCCESS)
        self.assertEqual(task.progress, 100)

    def test_pause_running_task_marks_cancel_requested(self):
        task = AsyncTaskExecution.objects.create(project=self.project, title="running", status=TaskStatus.RUNNING)
        response = self.client.post(reverse("async_tasks:task-action", kwargs={"task_id": task.id}), {"action": "pause"})
        task.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(task.cancel_requested)
