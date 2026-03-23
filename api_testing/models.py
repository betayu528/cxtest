from django.db import models


class HttpMethod(models.TextChoices):
    GET = "GET", "GET"
    POST = "POST", "POST"
    PUT = "PUT", "PUT"
    PATCH = "PATCH", "PATCH"
    DELETE = "DELETE", "DELETE"


class ApiProtocol(models.TextChoices):
    HTTP = "HTTP", "HTTP/HTTPS"
    TCP = "TCP", "TCP"
    WEBSOCKET = "WEBSOCKET", "WebSocket"


class ApiCollection(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="api_collections", on_delete=models.CASCADE)
    name = models.CharField("集合名称", max_length=128)
    description = models.TextField("描述", blank=True)
    source = models.CharField("来源", max_length=32, default="POSTMAN")
    raw_payload = models.JSONField("原始内容", default=dict, blank=True)
    uploaded_file = models.FileField("上传文件", upload_to="api_collections/", blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        verbose_name="创建人",
        related_name="api_collections",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "API 集合"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ApiEndpoint(models.Model):
    collection = models.ForeignKey(ApiCollection, verbose_name="集合", related_name="endpoints", on_delete=models.CASCADE)
    name = models.CharField("接口名称", max_length=128)
    method = models.CharField("请求方法", max_length=10, choices=HttpMethod.choices, default=HttpMethod.GET)
    path = models.CharField("接口路径", max_length=255)
    headers = models.JSONField("请求头", default=dict, blank=True)
    query_params = models.JSONField("Query 参数", default=dict, blank=True)
    request_body = models.JSONField("请求体", default=dict, blank=True)
    assertions = models.JSONField("断言", default=list, blank=True)

    class Meta:
        verbose_name = "API 接口"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ApiTestRecord(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="所属项目",
        related_name="api_test_records",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    protocol = models.CharField("协议", max_length=20, choices=ApiProtocol.choices, default=ApiProtocol.HTTP)
    name = models.CharField("测试名称", max_length=128)
    method = models.CharField("请求方法", max_length=10, choices=HttpMethod.choices, default=HttpMethod.GET, blank=True)
    target = models.CharField("目标地址", max_length=255)
    headers = models.JSONField("请求头", default=dict, blank=True)
    request_payload = models.TextField("请求内容", blank=True)
    response_status = models.CharField("响应状态", max_length=64, blank=True)
    response_headers = models.JSONField("响应头", default=dict, blank=True)
    response_text = models.TextField("响应文本", blank=True)
    response_hex = models.TextField("十六进制响应", blank=True)
    duration_ms = models.PositiveIntegerField("耗时毫秒", default=0)
    is_success = models.BooleanField("是否成功", default=True)
    error_message = models.TextField("错误信息", blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        verbose_name="执行人",
        related_name="api_test_records",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "API 测试记录"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} [{self.protocol}]"
