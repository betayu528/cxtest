from django.contrib import admin

from .models import Article, ArticleComment, ArticleFavorite, ArticleLike


class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "author", "content_format", "is_published", "is_recommended", "heat", "share_count", "published_at")
    list_filter = ("is_published", "is_recommended")
    search_fields = ("title", "summary", "content")
    inlines = [ArticleCommentInline]


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ("article", "author", "created_at")


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created_at")


@admin.register(ArticleFavorite)
class ArticleFavoriteAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "created_at")
