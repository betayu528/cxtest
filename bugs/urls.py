from django.urls import path

from .views import BugPostListView

app_name = "bugs"

urlpatterns = [
    path("", BugPostListView.as_view(), name="post-list"),
]
