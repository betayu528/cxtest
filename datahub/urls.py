from django.urls import path

from .views import DatasetListView

app_name = "datahub"

urlpatterns = [
    path("", DatasetListView.as_view(), name="dataset-list"),
]
