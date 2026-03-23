import time

from celery import shared_task
from django.db import close_old_connections

from notifications.models import Notification

from .models import AsyncTaskExecution, TaskStatus
from .services import CITriggerError, CITriggerService
from .task_actions import mark_failed, mark_paused, mark_progress, mark_running, mark_success


def get_task(task_id: int):
    close_old_connections()
    return AsyncTaskExecution.objects.select_related("integration", "created_by").get(pk=task_id)


@shared_task(bind=True, name="async_tasks.execute_platform_task")
def execute_platform_task(self, execution_id: int):
    task = get_task(execution_id)
    mark_running(task)

    if task.cancel_requested:
        mark_paused(task, "任务在执行前被暂停")
        return {"status": TaskStatus.PAUSED}

    mark_progress(task, 30, "开始准备执行参数")
    time.sleep(0.2)

    if task.cancel_requested:
        mark_paused(task, "任务执行中收到暂停请求")
        return {"status": TaskStatus.PAUSED}

    if task.integration_id:
        try:
            result = CITriggerService(task.integration).trigger(task)
        except CITriggerError as exc:
            mark_failed(task, str(exc), {"error": str(exc)})
            raise
        mark_progress(task, 80, "CI 平台已触发，等待回调")
        return {"status": task.status, "result": result}

    # 平台原生任务的最小执行器，后续可以替换为真实用例执行逻辑。
    time.sleep(0.2)
    if task.cancel_requested:
        mark_paused(task, "平台任务执行中收到暂停请求")
        return {"status": TaskStatus.PAUSED}

    result = {"message": "platform task executed"}
    mark_success(task, result, "平台任务执行完成")
    if task.created_by_id:
        Notification.objects.create(
            user=task.created_by,
            title=f"任务完成: {task.title}",
            content="Celery 任务已执行完成",
            category="TASK",
            metadata={"task_id": task.id},
        )
    return {"status": TaskStatus.SUCCESS, "result": result}
