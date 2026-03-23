from django.test import TestCase

from projects.models import Project

from .models import MockRule, MockService, ProtocolType
from .runtime import normalize_body, resolve_rule


class MockRuntimeTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(name="Demo", code="DEMO")
        self.service = MockService.objects.create(project=self.project, name="tcp", protocol=ProtocolType.TCP, port=9100)
        self.rule1 = MockRule.objects.create(service=self.service, name="ping", matcher={"contains": "ping"}, response_body="pong")
        self.rule2 = MockRule.objects.create(service=self.service, name="default", matcher={}, response_body="ok", sort_order=1)

    def test_resolve_rule_by_contains_matcher(self):
        rule = resolve_rule([self.rule1, self.rule2], "hello ping")
        self.assertEqual(rule.id, self.rule1.id)

    def test_normalize_body_for_json(self):
        payload = normalize_body({"status": "ok"}, "json")
        self.assertEqual(payload, b'{"status": "ok"}')
