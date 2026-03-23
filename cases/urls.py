from django.urls import path

from .views import (
    ProjectDocumentUploadView,
    SubProjectCreateView,
    TestCaseActionView,
    TestCaseCreateView,
    TestCaseDetailView,
    TestCaseExportView,
    TestCaseWorkspaceView,
)

app_name = "cases"

urlpatterns = [
    path("", TestCaseWorkspaceView.as_view(), name="case-list"),
    path("project/<int:project_id>/subproject/create/", SubProjectCreateView.as_view(), name="subproject-create"),
    path("project/<int:project_id>/create/", TestCaseCreateView.as_view(), name="case-create"),
    path("project/<int:project_id>/upload/", ProjectDocumentUploadView.as_view(), name="document-upload"),
    path("project/<int:project_id>/export/", TestCaseExportView.as_view(), name="case-export"),
    path("<int:pk>/", TestCaseDetailView.as_view(), name="case-detail"),
    path("<int:pk>/action/", TestCaseActionView.as_view(), name="case-action"),
]
