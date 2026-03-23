from django.db import models


class CasePriority(models.TextChoices):
    P0 = "P0", "P0"
    P1 = "P1", "P1"
    P2 = "P2", "P2"
    P3 = "P3", "P3"


class CaseType(models.TextChoices):
    AUTOMATED = "AUTOMATED", "自动化用例"
    MANUAL = "MANUAL", "非自动化用例"


class CaseSource(models.TextChoices):
    NATIVE = "NATIVE", "平台内建"
    XMIND = "XMIND", "XMind"
    PDF = "PDF", "PDF"
    EXCEL = "EXCEL", "Excel"
    POSTMAN = "POSTMAN", "Postman JSON"
    PYTEST = "PYTEST", "Pytest"


class TestSuite(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="suites", on_delete=models.CASCADE)
    name = models.CharField("用例集名称", max_length=128)
    description = models.TextField("描述", blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        verbose_name="创建人",
        related_name="created_suites",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "用例集"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class TestCase(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="cases", on_delete=models.CASCADE)
    suite = models.ForeignKey(
        TestSuite,
        verbose_name="所属用例集",
        related_name="cases",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name="父节点",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    case_id = models.CharField("用例 ID", max_length=64)
    name = models.CharField("用例名称", max_length=255)
    owner = models.ForeignKey(
        "accounts.User",
        verbose_name="负责人",
        related_name="owned_cases",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    description = models.TextField("用例描述", blank=True)
    expected_result = models.TextField("预期结果", blank=True)
    precondition = models.TextField("前置条件", blank=True)
    execution_env = models.CharField("执行环境", max_length=255, blank=True)
    priority = models.CharField("优先级", max_length=10, choices=CasePriority.choices, default=CasePriority.P2)
    case_type = models.CharField("用例类型", max_length=20, choices=CaseType.choices, default=CaseType.MANUAL)
    source = models.CharField("来源", max_length=20, choices=CaseSource.choices, default=CaseSource.NATIVE)
    repo_url = models.URLField("关联仓库", blank=True)
    postman_collection = models.JSONField("Postman 集合", default=dict, blank=True)
    pytest_node = models.CharField("Pytest 节点", max_length=255, blank=True)
    steps = models.JSONField("步骤", default=list, blank=True)
    tags = models.JSONField("标签", default=list, blank=True)
    is_active = models.BooleanField("有效", default=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "测试用例"
        verbose_name_plural = verbose_name
        unique_together = ("project", "case_id")
        ordering = ["project", "case_id"]

    def __str__(self):
        return f"{self.case_id} - {self.name}"


class CaseAttachment(models.Model):
    case = models.ForeignKey(TestCase, verbose_name="关联用例", related_name="attachments", on_delete=models.CASCADE)
    title = models.CharField("文件标题", max_length=128)
    file = models.FileField("附件", upload_to="case_attachments/")
    source = models.CharField("来源类型", max_length=20, choices=CaseSource.choices, default=CaseSource.NATIVE)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        verbose_name="上传人",
        related_name="uploaded_case_attachments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        verbose_name = "用例附件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class ProjectDocument(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属子项目", related_name="case_documents", on_delete=models.CASCADE)
    title = models.CharField("文件标题", max_length=128)
    file = models.FileField("文件", upload_to="project_case_documents/")
    source = models.CharField("文件类型", max_length=20, choices=CaseSource.choices)
    uploaded_by = models.ForeignKey(
        "accounts.User",
        verbose_name="上传人",
        related_name="uploaded_project_documents",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        verbose_name = "子项目文件"
        verbose_name_plural = verbose_name
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title
