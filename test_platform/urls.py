from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from test_platform.views import DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("projects/", include("projects.urls")),
    path("cases/", include("cases.urls")),
    path("api-testing/", include("api_testing.urls")),
    path("tasks/", include("async_tasks.urls")),
    path("mock/", include("mockserver.urls")),
    path("data/", include("datahub.urls")),
    path("bugs/", include("bugs.urls")),
    path("knowledge/", include("knowledge.urls")),
    path("notifications/", include("notifications.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
