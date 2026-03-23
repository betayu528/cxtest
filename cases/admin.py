from django.contrib import admin

from .models import CaseAttachment, ProjectDocument, TestCase, TestSuite


class CaseAttachmentInline(admin.TabularInline):
    model = CaseAttachment
    extra = 0


@admin.register(TestSuite)
class TestSuiteAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_by", "created_at")
    search_fields = ("name", "project__name")


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("case_id", "name", "project", "case_type", "priority", "owner", "source")
    search_fields = ("case_id", "name", "project__name")
    list_filter = ("case_type", "priority", "source", "project")
    inlines = [CaseAttachmentInline]


@admin.register(CaseAttachment)
class CaseAttachmentAdmin(admin.ModelAdmin):
    list_display = ("title", "case", "source", "uploaded_by", "uploaded_at")


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "source", "uploaded_by", "uploaded_at")
