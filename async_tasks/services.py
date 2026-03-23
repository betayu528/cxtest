import base64
import json
from urllib import error, parse, request

from django.urls import reverse
from django.utils import timezone

from .models import CIIntegration, CIProvider, TaskSource, TaskStatus


class CITriggerError(Exception):
    pass


class CITriggerService:
    def __init__(self, integration: CIIntegration):
        self.integration = integration

    def trigger(self, task):
        provider = self.integration.provider
        if provider == CIProvider.JENKINS:
            return self._trigger_jenkins(task)
        if provider == CIProvider.GITLAB_CI:
            return self._trigger_gitlab(task)
        raise CITriggerError(f"unsupported provider: {provider}")

    def _callback_url(self, task):
        base_url = self.integration.callback_base_url.rstrip("/")
        if not base_url:
            raise CITriggerError("callback_base_url is required")
        return f"{base_url}{reverse('async_tasks:task-callback', kwargs={'token': task.callback_token})}"

    def _build_url(self, path):
        base = self.integration.base_url.rstrip("/")
        if not path:
            return base
        return f"{base}/{path.lstrip('/')}"

    def _trigger_jenkins(self, task):
        job_name = self.integration.jenkins_job_name.strip()
        if not job_name:
            raise CITriggerError("jenkins_job_name is required")

        path = self.integration.trigger_path.strip() or f"job/{job_name}/buildWithParameters"
        payload = dict(self.integration.default_payload)
        payload.update(task.payload or {})
        payload["callback_url"] = self._callback_url(task)
        if self.integration.jenkins_token:
            payload.setdefault("token", self.integration.jenkins_token)

        headers = {}
        if self.integration.jenkins_crumb_url:
            crumb_headers = self._basic_auth_header()
            crumb_request = request.Request(self.integration.jenkins_crumb_url, headers=crumb_headers)
            with request.urlopen(crumb_request, timeout=20) as response:
                crumb_data = json.loads(response.read().decode("utf-8"))
            headers[crumb_data["crumbRequestField"]] = crumb_data["crumb"]

        headers.update(self._basic_auth_header())
        data = parse.urlencode(payload).encode("utf-8")
        req = request.Request(self._build_url(path), data=data, headers=headers, method="POST")
        try:
            with request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8", errors="ignore")
                queue_url = response.headers.get("Location", "")
        except error.HTTPError as exc:
            raise CITriggerError(f"jenkins trigger failed: {exc.code} {exc.reason}") from exc
        except error.URLError as exc:
            raise CITriggerError(f"jenkins trigger failed: {exc.reason}") from exc

        task.source = TaskSource.JENKINS
        task.status = TaskStatus.RUNNING
        task.started_at = timezone.now()
        task.trigger_url = self._build_url(path)
        task.external_job_name = job_name
        task.result = {"queue_url": queue_url, "response": body}
        task.save(
            update_fields=[
                "source",
                "status",
                "started_at",
                "trigger_url",
                "external_job_name",
                "result",
                "updated_at",
            ]
        )
        return {"queue_url": queue_url, "response": body}

    def _trigger_gitlab(self, task):
        project_id = self.integration.gitlab_project_id.strip()
        trigger_token = self.integration.gitlab_trigger_token.strip()
        if not project_id or not trigger_token:
            raise CITriggerError("gitlab_project_id and gitlab_trigger_token are required")

        path = self.integration.trigger_path.strip() or f"api/v4/projects/{parse.quote(project_id, safe='')}/trigger/pipeline"
        payload = {
            "token": trigger_token,
            "ref": self.integration.gitlab_ref or "main",
        }
        merged_payload = dict(self.integration.default_payload)
        merged_payload.update(task.payload or {})
        merged_payload["callback_url"] = self._callback_url(task)
        for key, value in merged_payload.items():
            payload[f"variables[{key}]"] = json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value

        headers = {}
        if self.integration.gitlab_private_token:
            headers["PRIVATE-TOKEN"] = self.integration.gitlab_private_token

        req = request.Request(
            self._build_url(path),
            data=parse.urlencode(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body or "{}")
        except error.HTTPError as exc:
            raise CITriggerError(f"gitlab trigger failed: {exc.code} {exc.reason}") from exc
        except error.URLError as exc:
            raise CITriggerError(f"gitlab trigger failed: {exc.reason}") from exc

        task.source = TaskSource.GITLAB_CI
        task.status = TaskStatus.RUNNING
        task.started_at = timezone.now()
        task.trigger_url = self._build_url(path)
        task.external_job_name = str(data.get("ref", payload["ref"]))
        task.external_build_id = str(data.get("id", ""))
        task.result = data
        task.save(
            update_fields=[
                "source",
                "status",
                "started_at",
                "trigger_url",
                "external_job_name",
                "external_build_id",
                "result",
                "updated_at",
            ]
        )
        return data

    def _basic_auth_header(self):
        if not self.integration.jenkins_username or not self.integration.jenkins_api_token:
            return {}
        raw = f"{self.integration.jenkins_username}:{self.integration.jenkins_api_token}".encode("utf-8")
        token = base64.b64encode(raw).decode("ascii")
        return {"Authorization": f"Basic {token}"}
