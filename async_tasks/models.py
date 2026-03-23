import secrets

from django.db import models


class TaskSource(models.TextChoices):
    PLATFORM = "PLATFORM", "平台任务"
    JENKINS = "JENKINS", "Jenkins"
    GITLAB_CI = "GITLAB_CI", "GitLab CI"


class TaskType(models.TextChoices):
    SUITE_RUN = "SUITE_RUN", "用例集执行"
    ENV_DEPLOY = "ENV_DEPLOY", "环境部署"
    API_RUN = "API_RUN", "API 执行"


class TaskStatus(models.TextChoices):
    PENDING = "PENDING", "待执行"
    QUEUED = "QUEUED", "排队中"
    RUNNING = "RUNNING", "执行中"
    PAUSED = "PAUSED", "已暂停"
    SUCCESS = "SUCCESS", "成功"
    FAILED = "FAILED", "失败"
    CALLBACK = "CALLBACK", "回调中"


class CIProvider(models.TextChoices):
    JENKINS = "JENKINS", "Jenkins"
    GITLAB_CI = "GITLAB_CI", "GitLab CI"


def generate_callback_token():
    return secrets.token_hex(16)


class CIIntegration(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="ci_integrations", on_delete=models.CASCADE)
    name = models.CharField("集成名称", max_length=128)
    provider = models.CharField("CI 平台", max_length=32, choices=CIProvider.choices, default=CIProvider.JENKINS)
    base_url = models.URLField("基础地址")
    trigger_path = models.CharField("触发路径", max_length=255, blank=True)
    callback_base_url = models.URLField("平台回调前缀", blank=True)
    jenkins_job_name = models.CharField("Jenkins Job", max_length=128, blank=True)
    jenkins_token = models.CharField("Jenkins Token", max_length=255, blank=True)
    jenkins_username = models.CharField("Jenkins 用户名", max_length=128, blank=True)
    jenkins_api_token = models.CharField("Jenkins API Token", max_length=255, blank=True)
    jenkins_crumb_url = models.URLField("Jenkins Crumb 地址", blank=True)
    gitlab_project_id = models.CharField("GitLab Project ID", max_length=128, blank=True)
    gitlab_ref = models.CharField("Git 分支", max_length=128, blank=True, default="main")
    gitlab_trigger_token = models.CharField("GitLab Trigger Token", max_length=255, blank=True)
    gitlab_private_token = models.CharField("GitLab Private Token", max_length=255, blank=True)
    default_payload = models.JSONField("默认参数", default=dict, blank=True)
    is_active = models.BooleanField("启用", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "CI 集成"
        verbose_name_plural = verbose_name
        ordering = ["project__name", "name"]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class AsyncTaskExecution(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="所属项目",
        related_name="task_executions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    task_type = models.CharField("任务类型", max_length=32, choices=TaskType.choices, default=TaskType.SUITE_RUN)
    source = models.CharField("任务来源", max_length=32, choices=TaskSource.choices, default=TaskSource.PLATFORM)
    status = models.CharField("任务状态", max_length=16, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    integration = models.ForeignKey(
        CIIntegration,
        verbose_name="CI 集成",
        related_name="executions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    title = models.CharField("任务标题", max_length=255)
    description = models.TextField("任务说明", blank=True)
    external_job_name = models.CharField("外部任务名", max_length=128, blank=True)
    external_build_id = models.CharField("外部构建号", max_length=128, blank=True)
    trigger_url = models.URLField("触发地址", blank=True)
    callback_token = models.CharField("回调令牌", max_length=64, unique=True, default=generate_callback_token)
    celery_task_id = models.CharField("Celery 任务 ID", max_length=128, blank=True)
    queue_name = models.CharField("队列名称", max_length=64, default="platform")
    progress = models.PositiveIntegerField("执行进度", default=0)
    action_logs = models.JSONField("动作日志", default=list, blank=True)
    cancel_requested = models.BooleanField("请求暂停", default=False)
    payload = models.JSONField("触发参数", default=dict, blank=True)
    result = models.JSONField("执行结果", default=dict, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        verbose_name="触发人",
        related_name="task_executions",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    finished_at = models.DateTimeField("完成时间", null=True, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "异步任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
