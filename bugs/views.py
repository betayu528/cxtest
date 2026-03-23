from django.views.generic import ListView

from .models import BugPost


class BugPostListView(ListView):
    model = BugPost
    template_name = "bugs/post_list.html"
    context_object_name = "posts"
    queryset = BugPost.objects.select_related("project", "author").prefetch_related("comments").order_by(
        "-is_pinned",
        "-heat",
        "-updated_at",
    )
