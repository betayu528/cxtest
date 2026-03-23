from django.views.generic import ListView

from .models import TestDataset


class DatasetListView(ListView):
    model = TestDataset
    template_name = "datahub/dataset_list.html"
    context_object_name = "datasets"
    queryset = TestDataset.objects.select_related("project", "created_by").order_by("-created_at")
