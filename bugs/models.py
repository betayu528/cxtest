from django.db import models


class BugPost(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="所属项目",
        related_name="bug_posts",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField("标题", max_length=255)
    content = models.TextField("内容")
    author = models.ForeignKey(
        "accounts.User",
        verbose_name="作者",
        related_name="bug_posts",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_pinned = models.BooleanField("置顶", default=False)
    heat = models.PositiveIntegerField("热度", default=0)
    view_count = models.PositiveIntegerField("浏览量", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "历史 Bug 帖子"
        verbose_name_plural = verbose_name
        ordering = ["-is_pinned", "-heat", "-updated_at"]

    def __str__(self):
        return self.title


class BugComment(models.Model):
    post = models.ForeignKey(BugPost, verbose_name="帖子", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "accounts.User",
        verbose_name="作者",
        related_name="bug_comments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    content = models.TextField("评论内容")
    parent = models.ForeignKey(
        "self",
        verbose_name="父评论",
        related_name="replies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "Bug 评论"
        verbose_name_plural = verbose_name
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.post.title}#{self.id}"
