from django.contrib import admin

from .models import TestDataRecord, TestDataset


class TestDataRecordInline(admin.TabularInline):
    model = TestDataRecord
    extra = 0


@admin.register(TestDataset)
class TestDatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_by", "created_at")
    search_fields = ("name", "project__name")
    inlines = [TestDataRecordInline]


@admin.register(TestDataRecord)
class TestDataRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "dataset", "remark", "created_at")
