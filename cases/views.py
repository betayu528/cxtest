import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, TemplateView

from projects.models import Project

from .forms import ProjectDocumentForm, SubProjectForm, TestCaseForm
from .models import ProjectDocument, TestCase


class TestCaseWorkspaceView(TemplateView):
    template_name = "cases/case_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.GET.get("project")
        selected_project = None
        if project_id:
            selected_project = Project.objects.filter(pk=project_id).select_related("parent", "owner").first()

        root_projects = Project.objects.filter(parent__isnull=True).prefetch_related("children").order_by("name")
        case_queryset = TestCase.objects.select_related("project", "owner", "suite").filter(parent__isnull=True)
        document_queryset = ProjectDocument.objects.select_related("project", "uploaded_by")
        if selected_project:
            case_queryset = case_queryset.filter(project=selected_project)
            document_queryset = document_queryset.filter(project=selected_project)

        context.update(
            {
                "root_projects": root_projects,
                "selected_project": selected_project,
                "cases": case_queryset.order_by("case_id"),
                "documents": document_queryset.order_by("-uploaded_at"),
                "subproject_form": SubProjectForm(),
                "case_form": TestCaseForm(),
                "document_form": ProjectDocumentForm(),
            }
        )
        return context


class SubProjectCreateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        parent = get_object_or_404(Project, pk=project_id)
        form = SubProjectForm(request.POST)
        if form.is_valid():
            subproject = form.save(commit=False)
            subproject.parent = parent
            subproject.owner = request.user
            subproject.save()
            messages.success(request, "子项目已创建")
            return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={subproject.id}")
        messages.error(request, "子项目创建失败")
        return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={parent.id}")


class TestCaseCreateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        form = TestCaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            case.project = project
            case.save()
            messages.success(request, "测试用例已新增")
        else:
            messages.error(request, "测试用例新增失败")
        return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={project.id}")


class ProjectDocumentUploadView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        form = ProjectDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            document.save()
            messages.success(request, "文件已上传")
        else:
            messages.error(request, "文件上传失败")
        return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={project.id}")


class TestCaseDetailView(DetailView):
    model = TestCase
    template_name = "cases/case_detail.html"
    context_object_name = "case"

    def get_queryset(self):
        return TestCase.objects.select_related("project", "owner", "suite").prefetch_related("attachments")


class TestCaseExportView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        selected_ids = request.POST.getlist("case_ids")
        queryset = TestCase.objects.filter(project=project)
        if selected_ids:
            queryset = queryset.filter(id__in=selected_ids)

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = f'attachment; filename="cases-{project.code}.csv"'
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(["用例ID", "用例名称", "负责人", "用例描述", "预期结果", "前置条件", "执行环境", "优先级", "状态"])
        for case in queryset.order_by("case_id"):
            writer.writerow(
                [
                    case.case_id,
                    case.name,
                    case.owner or "",
                    case.description,
                    case.expected_result,
                    case.precondition,
                    case.execution_env,
                    case.priority,
                    "启用" if case.is_active else "禁用",
                ]
            )
        return response


class TestCaseActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        case = get_object_or_404(TestCase, pk=pk)
        action = request.POST.get("action")
        if action == "disable":
            case.is_active = False
            case.save(update_fields=["is_active", "updated_at"])
            messages.success(request, "用例已禁用")
        elif action == "enable":
            case.is_active = True
            case.save(update_fields=["is_active", "updated_at"])
            messages.success(request, "用例已启用")
        elif action == "delete":
            project_id = case.project_id
            case.delete()
            messages.success(request, "用例已删除")
            return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={project_id}")
        return HttpResponseRedirect(f"{reverse('cases:case-list')}?project={case.project_id}")
