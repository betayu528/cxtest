from django.db import models


class ProtocolType(models.TextChoices):
    HTTP = "HTTP", "HTTP"
    TCP = "TCP", "TCP"
    UDP = "UDP", "UDP"
    WEBSOCKET = "WEBSOCKET", "WebSocket"


class MockService(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="mock_services", on_delete=models.CASCADE)
    name = models.CharField("服务名称", max_length=128)
    protocol = models.CharField("协议", max_length=16, choices=ProtocolType.choices, default=ProtocolType.HTTP)
    host = models.CharField("监听地址", max_length=64, default="0.0.0.0")
    port = models.PositiveIntegerField("端口", default=8001)
    route = models.CharField("HTTP 路由", max_length=255, blank=True)
    is_enabled = models.BooleanField("启用", default=True)
    config = models.JSONField("协议配置", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "Mock 服务"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name} [{self.protocol}]"


class MockRule(models.Model):
    service = models.ForeignKey(MockService, verbose_name="所属服务", related_name="rules", on_delete=models.CASCADE)
    name = models.CharField("规则名称", max_length=128)
    matcher = models.JSONField("匹配条件", default=dict, blank=True)
    response_status = models.PositiveIntegerField("响应状态", default=200)
    response_headers = models.JSONField("响应头", default=dict, blank=True)
    response_body = models.JSONField("响应体", default=dict, blank=True)
    response_delay_ms = models.PositiveIntegerField("延迟毫秒", default=0)
    sort_order = models.PositiveIntegerField("顺序", default=0)

    class Meta:
        verbose_name = "Mock 规则"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.name
