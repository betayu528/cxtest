from django.utils import timezone

from .models import AsyncTaskExecution, TaskStatus


class TaskActionError(Exception):
    pass


def append_log(task: AsyncTaskExecution, action: str, message: str):
    logs = list(task.action_logs or [])
    logs.append(
        {
            "action": action,
            "message": message,
            "at": timezone.now().isoformat(),
        }
    )
    task.action_logs = logs[-30:]


def mark_queued(task: AsyncTaskExecution, celery_task_id: str):
    task.status = TaskStatus.QUEUED
    task.celery_task_id = celery_task_id
    task.progress = 0
    task.cancel_requested = False
    append_log(task, "QUEUE", "任务已进入 Celery 队列")
    task.save(update_fields=["status", "celery_task_id", "progress", "cancel_requested", "action_logs", "updated_at"])


def mark_running(task: AsyncTaskExecution, message="任务开始执行"):
    task.status = TaskStatus.RUNNING
    task.started_at = task.started_at or timezone.now()
    task.progress = max(task.progress, 10)
    append_log(task, "RUN", message)
    task.save(update_fields=["status", "started_at", "progress", "action_logs", "updated_at"])


def mark_progress(task: AsyncTaskExecution, progress: int, message: str):
    task.progress = max(0, min(100, progress))
    append_log(task, "PROGRESS", message)
    task.save(update_fields=["progress", "action_logs", "updated_at"])


def mark_success(task: AsyncTaskExecution, result=None, message="任务执行成功"):
    task.status = TaskStatus.SUCCESS
    task.finished_at = timezone.now()
    task.progress = 100
    if result is not None:
        task.result = result
    append_log(task, "SUCCESS", message)
    task.save(update_fields=["status", "finished_at", "progress", "result", "action_logs", "updated_at"])


def mark_failed(task: AsyncTaskExecution, message: str, result=None):
    task.status = TaskStatus.FAILED
    task.finished_at = timezone.now()
    if result is not None:
        task.result = result
    append_log(task, "FAILED", message)
    task.save(update_fields=["status", "finished_at", "result", "action_logs", "updated_at"])


def mark_paused(task: AsyncTaskExecution, message="任务已暂停"):
    task.status = TaskStatus.PAUSED
    task.finished_at = timezone.now()
    task.cancel_requested = False
    append_log(task, "PAUSE", message)
    task.save(update_fields=["status", "finished_at", "cancel_requested", "action_logs", "updated_at"])


def request_pause(task: AsyncTaskExecution):
    if task.status not in {TaskStatus.RUNNING, TaskStatus.QUEUED}:
        raise TaskActionError("only running or queued tasks can be paused")
    task.cancel_requested = True
    append_log(task, "PAUSE_REQUEST", "已请求暂停任务")
    task.save(update_fields=["cancel_requested", "action_logs", "updated_at"])


def ensure_startable(task: AsyncTaskExecution):
    if task.status not in {TaskStatus.PENDING, TaskStatus.FAILED, TaskStatus.PAUSED}:
        raise TaskActionError("task is not startable")


def ensure_retryable(task: AsyncTaskExecution):
    if task.status != TaskStatus.FAILED:
        raise TaskActionError("only failed tasks can be retried")
