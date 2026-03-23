from django.contrib import admin

from .models import ApiCollection, ApiEndpoint, ApiTestRecord


class ApiEndpointInline(admin.TabularInline):
    model = ApiEndpoint
    extra = 0


@admin.register(ApiCollection)
class ApiCollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "source", "created_by", "created_at")
    search_fields = ("name", "project__name")
    inlines = [ApiEndpointInline]


@admin.register(ApiEndpoint)
class ApiEndpointAdmin(admin.ModelAdmin):
    list_display = ("name", "collection", "method", "path")
    search_fields = ("name", "path", "collection__name")


@admin.register(ApiTestRecord)
class ApiTestRecordAdmin(admin.ModelAdmin):
    list_display = ("name", "protocol", "project", "response_status", "duration_ms", "is_success", "created_at")
    list_filter = ("protocol", "is_success")
    search_fields = ("name", "target", "project__name")
