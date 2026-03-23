import json

from celery import current_app
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from notifications.models import Notification

from .models import AsyncTaskExecution, CIIntegration, TaskStatus
from .task_actions import TaskActionError, ensure_retryable, ensure_startable, mark_queued, request_pause
from .tasks import execute_platform_task


def enqueue_execution(task: AsyncTaskExecution):
    celery_task = execute_platform_task.delay(task.id)
    if not current_app.conf.task_always_eager:
        mark_queued(task, celery_task.id)
    else:
        task.celery_task_id = celery_task.id or task.celery_task_id
        task.save(update_fields=["celery_task_id", "updated_at"])
    return celery_task


class AsyncTaskListView(ListView):
    model = AsyncTaskExecution
    template_name = "async_tasks/task_list.html"
    context_object_name = "tasks"
    queryset = AsyncTaskExecution.objects.select_related("project", "created_by", "integration").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["integrations"] = CIIntegration.objects.select_related("project").filter(is_active=True).order_by("project__name", "name")
        return context


class CIIntegrationTriggerView(View):
    http_method_names = ["post"]

    def post(self, request, integration_id):
        integration = CIIntegration.objects.select_related("project").filter(pk=integration_id, is_active=True).first()
        if integration is None:
            return JsonResponse({"detail": "integration not found"}, status=404)

        try:
            body = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "invalid json body"}, status=400)

        task = AsyncTaskExecution.objects.create(
            project=integration.project,
            integration=integration,
            task_type=body.get("task_type") or "SUITE_RUN",
            title=body.get("title") or f"{integration.name} 触发任务",
            description=body.get("description", ""),
            created_by=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            payload=body.get("payload", {}),
            status=TaskStatus.PENDING,
        )
        celery_task = enqueue_execution(task)
        return JsonResponse({"detail": "queued", "task_id": task.id, "callback_token": task.callback_token, "celery_task_id": celery_task.id})


class AsyncTaskActionView(View):
    http_method_names = ["post"]

    def post(self, request, task_id):
        task = get_object_or_404(AsyncTaskExecution, pk=task_id)
        action = request.POST.get("action") or request.GET.get("action")

        try:
            if action == "start":
                ensure_startable(task)
                task.finished_at = None
                task.result = {}
                task.progress = 0
                task.celery_task_id = ""
                task.cancel_requested = False
                task.save(
                    update_fields=[
                        "finished_at",
                        "result",
                        "progress",
                        "celery_task_id",
                        "cancel_requested",
                        "updated_at",
                    ]
                )
                enqueue_execution(task)
            elif action == "retry":
                ensure_retryable(task)
                task.status = TaskStatus.PENDING
                task.finished_at = None
                task.result = {}
                task.progress = 0
                task.celery_task_id = ""
                task.cancel_requested = False
                task.save(
                    update_fields=["status", "finished_at", "result", "progress", "celery_task_id", "cancel_requested", "updated_at"]
                )
                enqueue_execution(task)
            elif action == "pause":
                request_pause(task)
            else:
                raise TaskActionError("unsupported action")
        except TaskActionError as exc:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"detail": str(exc)}, status=400)
            return HttpResponseRedirect(reverse("async_tasks:task-list"))

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            task.refresh_from_db()
            return JsonResponse({"detail": "ok", "status": task.status, "progress": task.progress})
        return HttpResponseRedirect(reverse("async_tasks:task-list"))


class AsyncTaskCallbackView(View):
    http_method_names = ["post"]

    def post(self, request, token):
        task = AsyncTaskExecution.objects.filter(callback_token=token).select_related("created_by").first()
        if task is None:
            return JsonResponse({"detail": "task not found"}, status=404)

        try:
            payload = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return JsonResponse({"detail": "invalid json body"}, status=400)
        task.status = payload.get("status", TaskStatus.SUCCESS)
        task.result = payload
        task.finished_at = timezone.now()
        task.progress = 100 if task.status == TaskStatus.SUCCESS else task.progress
        task.save(update_fields=["status", "result", "finished_at", "progress", "updated_at"])

        if task.created_by:
            Notification.objects.create(
                user=task.created_by,
                title=f"任务完成: {task.title}",
                content=f"任务状态已更新为 {task.get_status_display()}",
                category="TASK",
                metadata={"task_id": task.id, "callback_payload": payload},
            )

        return JsonResponse({"detail": "callback accepted", "task_id": task.id})
