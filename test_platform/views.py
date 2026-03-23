from django.views.generic import TemplateView

from api_testing.models import ApiCollection
from async_tasks.models import AsyncTaskExecution
from bugs.models import BugPost
from cases.models import TestCase
from knowledge.models import Article
from notifications.models import Notification
from projects.models import Project


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "project_count": Project.objects.count(),
                "case_count": TestCase.objects.count(),
                "api_collection_count": ApiCollection.objects.count(),
                "task_count": AsyncTaskExecution.objects.count(),
                "bug_count": BugPost.objects.count(),
                "article_count": Article.objects.count(),
                "notification_count": Notification.objects.count(),
                "latest_tasks": AsyncTaskExecution.objects.select_related("project").order_by("-created_at")[:5],
                "hot_bugs": BugPost.objects.order_by("-is_pinned", "-heat", "-updated_at")[:5],
                "recommended_articles": Article.objects.order_by("-is_recommended", "-heat", "-published_at")[:5],
            }
        )
        return context
