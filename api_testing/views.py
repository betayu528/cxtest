from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from .forms import ApiDebugForm
from .models import ApiCollection, ApiTestRecord
from .services import ApiDebugService


class ApiCollectionListView(TemplateView):
    template_name = "api_testing/collection_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collections"] = ApiCollection.objects.select_related("project", "created_by").order_by("-created_at")
        context["form"] = ApiDebugForm()
        context["records"] = ApiTestRecord.objects.select_related("project", "created_by").order_by("-created_at")[:10]
        context["latest_result"] = None
        return context

    def post(self, request, *args, **kwargs):
        form = ApiDebugForm(request.POST)
        collections = ApiCollection.objects.select_related("project", "created_by").order_by("-created_at")
        records = ApiTestRecord.objects.select_related("project", "created_by").order_by("-created_at")[:10]
        latest_result = None
        if form.is_valid():
            service = ApiDebugService(request.user)
            latest_result = service.execute(form.cleaned_data)
            ApiTestRecord.objects.create(
                project=form.cleaned_data.get("project"),
                protocol=form.cleaned_data["protocol"],
                name=form.cleaned_data["name"],
                method=form.cleaned_data.get("method") or "",
                target=form.cleaned_data["target"],
                headers=latest_result["headers"],
                request_payload=form.cleaned_data.get("request_payload", ""),
                response_status=latest_result["response_status"],
                response_headers=latest_result["response_headers"],
                response_text=latest_result["response_text"],
                response_hex=latest_result["response_hex"],
                duration_ms=latest_result["duration_ms"],
                is_success=latest_result["is_success"],
                error_message=latest_result["error_message"],
                created_by=request.user if request.user.is_authenticated else None,
            )
            if latest_result["is_success"]:
                messages.success(request, "协议测试执行完成")
            else:
                messages.error(request, f"协议测试失败: {latest_result['error_message']}")
        return self.render_to_response(
            {
                "collections": collections,
                "form": form,
                "records": records,
                "latest_result": latest_result,
            }
        )
