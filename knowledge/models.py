from django.db import models


class ArticleContentFormat(models.TextChoices):
    MARKDOWN = "MARKDOWN", "Markdown"
    RICHTEXT = "RICHTEXT", "富文本"


class Article(models.Model):
    project = models.ForeignKey(
        "projects.Project",
        verbose_name="所属项目",
        related_name="articles",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    title = models.CharField("标题", max_length=255)
    summary = models.CharField("摘要", max_length=255, blank=True)
    content = models.TextField("正文")
    content_format = models.CharField("内容格式", max_length=20, choices=ArticleContentFormat.choices, default=ArticleContentFormat.MARKDOWN)
    author = models.ForeignKey(
        "accounts.User",
        verbose_name="作者",
        related_name="articles",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_published = models.BooleanField("已发布", default=True)
    is_recommended = models.BooleanField("管理员推荐", default=False)
    heat = models.PositiveIntegerField("热度", default=0)
    share_count = models.PositiveIntegerField("分享数", default=0)
    published_at = models.DateTimeField("发布时间", auto_now_add=True)

    class Meta:
        verbose_name = "知识文章"
        verbose_name_plural = verbose_name
        ordering = ["-is_recommended", "-heat", "-published_at"]

    def __str__(self):
        return self.title


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, verbose_name="文章", related_name="comments", on_delete=models.CASCADE)
    author = models.ForeignKey(
        "accounts.User",
        verbose_name="作者",
        related_name="article_comments",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    content = models.TextField("评论")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "文章评论"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.article.title}#{self.id}"


class ArticleLike(models.Model):
    article = models.ForeignKey(Article, verbose_name="文章", related_name="likes", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", verbose_name="用户", related_name="article_likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "文章点赞"
        verbose_name_plural = verbose_name
        unique_together = ("article", "user")


class ArticleFavorite(models.Model):
    article = models.ForeignKey(Article, verbose_name="文章", related_name="favorites", on_delete=models.CASCADE)
    user = models.ForeignKey("accounts.User", verbose_name="用户", related_name="article_favorites", on_delete=models.CASCADE)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        verbose_name = "文章收藏"
        verbose_name_plural = verbose_name
        unique_together = ("article", "user")
