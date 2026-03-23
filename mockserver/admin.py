from django.contrib import admin

from .models import MockRule, MockService


class MockRuleInline(admin.TabularInline):
    model = MockRule
    extra = 0


@admin.register(MockService)
class MockServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "protocol", "host", "port", "route", "is_enabled")
    list_filter = ("protocol", "is_enabled")
    search_fields = ("name", "route", "project__name")
    inlines = [MockRuleInline]


@admin.register(MockRule)
class MockRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "service", "response_status", "response_delay_ms", "sort_order")
