from django.db import models


class TestDataset(models.Model):
    project = models.ForeignKey("projects.Project", verbose_name="所属项目", related_name="datasets", on_delete=models.CASCADE)
    name = models.CharField("数据集名称", max_length=128)
    description = models.TextField("描述", blank=True)
    schema = models.JSONField("字段定义", default=list, blank=True)
    tags = models.JSONField("标签", default=list, blank=True)
    created_by = models.ForeignKey(
        "accounts.User",
        verbose_name="创建人",
        related_name="datasets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "测试数据集"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class TestDataRecord(models.Model):
    dataset = models.ForeignKey(TestDataset, verbose_name="数据集", related_name="records", on_delete=models.CASCADE)
    data = models.JSONField("数据内容", default=dict, blank=True)
    remark = models.CharField("备注", max_length=255, blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "测试数据"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.dataset.name}#{self.id}"
