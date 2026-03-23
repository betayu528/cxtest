from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from projects.models import Project

from .models import TestCase as CaseModel


class CaseWorkspaceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester", password="pass123456", role=UserRole.TEST)
        self.root_project = Project.objects.create(name="Root", code="ROOT")
        self.sub_project = Project.objects.create(name="Sub", code="SUB", parent=self.root_project)
        self.case = CaseModel.objects.create(project=self.sub_project, case_id="CASE-1", name="demo case")

    def test_workspace_page_can_filter_by_project(self):
        response = self.client.get(reverse("cases:case-list"), {"project": self.sub_project.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "demo case")

    def test_case_detail_page(self):
        response = self.client.get(reverse("cases:case-detail", kwargs={"pk": self.case.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CASE-1")

    def test_export_cases(self):
        response = self.client.post(reverse("cases:case-export", kwargs={"project_id": self.sub_project.id}), {"case_ids": [self.case.id]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("CASE-1", response.content.decode("utf-8-sig"))

    def test_disable_case(self):
        self.client.login(username="tester", password="pass123456")
        response = self.client.post(reverse("cases:case-action", kwargs={"pk": self.case.id}), {"action": "disable"})
        self.case.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.case.is_active)
