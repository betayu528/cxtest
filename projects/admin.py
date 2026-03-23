from django.contrib import admin

from .models import Environment, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "owner", "parent", "is_active", "updated_at")
    search_fields = ("name", "code")
    list_filter = ("is_active",)
    filter_horizontal = ("members",)


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "base_url")
    search_fields = ("name", "project__name")
