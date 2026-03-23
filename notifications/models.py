from django.db import models


class Notification(models.Model):
    CATEGORY_CHOICES = [
        ("BLOG", "博客"),
        ("COMMENT", "评论"),
        ("TASK", "任务"),
        ("SYSTEM", "系统"),
    ]

    user = models.ForeignKey("accounts.User", verbose_name="用户", related_name="notifications", on_delete=models.CASCADE)
    title = models.CharField("标题", max_length=128)
    content = models.TextField("内容")
    category = models.CharField("类型", max_length=20, choices=CATEGORY_CHOICES, default="SYSTEM")
    is_read = models.BooleanField("已读", default=False)
    metadata = models.JSONField("扩展信息", default=dict, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ["is_read", "-created_at"]

    def __str__(self):
        return self.title
