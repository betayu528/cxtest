import time

from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView

from .models import MockService, ProtocolType


class MockServiceListView(ListView):
    model = MockService
    template_name = "mockserver/service_list.html"
    context_object_name = "services"
    queryset = MockService.objects.select_related("project").prefetch_related("rules").order_by("project__name", "name")


class HttpMockDispatchView(View):
    def dispatch(self, request, *args, **kwargs):
        route = "/" + kwargs["route"]
        service = (
            MockService.objects.filter(protocol=ProtocolType.HTTP, route=route, is_enabled=True)
            .prefetch_related("rules")
            .first()
        )
        if service is None:
            return JsonResponse({"detail": "mock service not found", "route": route}, status=404)

        rule = service.rules.first()
        if rule is None:
            return JsonResponse({"detail": "mock rule not configured", "service": service.name}, status=404)

        if rule.response_delay_ms:
            time.sleep(rule.response_delay_ms / 1000)

        response = JsonResponse(rule.response_body, status=rule.response_status, safe=isinstance(rule.response_body, dict))
        for key, value in rule.response_headers.items():
            response[key] = value
        return response
