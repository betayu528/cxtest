from django.views.generic import ListView

from .models import Notification


class NotificationListView(ListView):
    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    queryset = Notification.objects.select_related("user").order_by("is_read", "-created_at")
