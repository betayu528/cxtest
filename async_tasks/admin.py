from django.contrib import admin

from .models import AsyncTaskExecution, CIIntegration


@admin.register(CIIntegration)
class CIIntegrationAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "provider", "base_url", "is_active", "updated_at")
    list_filter = ("provider", "is_active")
    search_fields = ("name", "project__name", "base_url")


@admin.register(AsyncTaskExecution)
class AsyncTaskExecutionAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "integration", "task_type", "source", "status", "progress", "created_by", "created_at")
    search_fields = ("title", "external_job_name", "external_build_id")
    list_filter = ("task_type", "source", "status")
