from django.urls import path

from .views import AsyncTaskActionView, AsyncTaskCallbackView, AsyncTaskListView, CIIntegrationTriggerView

app_name = "async_tasks"

urlpatterns = [
    path("", AsyncTaskListView.as_view(), name="task-list"),
    path("trigger/<int:integration_id>/", CIIntegrationTriggerView.as_view(), name="integration-trigger"),
    path("action/<int:task_id>/", AsyncTaskActionView.as_view(), name="task-action"),
    path("callback/<str:token>/", AsyncTaskCallbackView.as_view(), name="task-callback"),
]
