from django.urls import path

from .views import ApiCollectionListView

app_name = "api_testing"

urlpatterns = [
    path("", ApiCollectionListView.as_view(), name="collection-list"),
]
