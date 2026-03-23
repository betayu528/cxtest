from django.urls import path

from .views import HttpMockDispatchView, MockServiceListView

app_name = "mockserver"

urlpatterns = [
    path("", MockServiceListView.as_view(), name="service-list"),
    path("http/<path:route>/", HttpMockDispatchView.as_view(), name="http-dispatch"),
]
