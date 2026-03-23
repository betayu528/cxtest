from django.db import models


class Project(models.Model):
    name = models.CharField("项目名称", max_length=128)
    code = models.CharField("项目编码", max_length=64, unique=True)
    description = models.TextField("项目描述", blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="父项目",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        "accounts.User",
        verbose_name="项目负责人",
        related_name="owned_projects",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    members = models.ManyToManyField("accounts.User", verbose_name="项目成员", related_name="projects", blank=True)
    repo_url = models.URLField("代码仓地址", blank=True)
    is_active = models.BooleanField("启用中", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        ordering = ["name"]

    def __str__(self):
        return self.name


class Environment(models.Model):
    project = models.ForeignKey(Project, verbose_name="所属项目", related_name="environments", on_delete=models.CASCADE)
    name = models.CharField("环境名称", max_length=64)
    base_url = models.URLField("基础地址", blank=True)
    variables = models.JSONField("环境变量", default=dict, blank=True)
    remark = models.TextField("备注", blank=True)

    class Meta:
        verbose_name = "环境"
        verbose_name_plural = verbose_name
        unique_together = ("project", "name")

    def __str__(self):
        return f"{self.project.name} - {self.name}"
