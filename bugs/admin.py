from django.contrib import admin

from .models import BugComment, BugPost


class BugCommentInline(admin.TabularInline):
    model = BugComment
    extra = 0


@admin.register(BugPost)
class BugPostAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "author", "is_pinned", "heat", "updated_at")
    list_filter = ("is_pinned", "project")
    search_fields = ("title", "content")
    inlines = [BugCommentInline]


@admin.register(BugComment)
class BugCommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "created_at")
