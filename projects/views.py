from django.views.generic import ListView

from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    queryset = Project.objects.select_related("parent", "owner").prefetch_related("members").order_by("name")
