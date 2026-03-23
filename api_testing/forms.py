from django import forms

from projects.models import Project

from .models import ApiProtocol, HttpMethod


class ApiDebugForm(forms.Form):
    project = forms.ModelChoiceField(queryset=Project.objects.order_by("name"), required=False, label="所属项目")
    name = forms.CharField(label="测试名称", max_length=128)
    protocol = forms.ChoiceField(label="协议", choices=ApiProtocol.choices, initial=ApiProtocol.HTTP)
    method = forms.ChoiceField(label="HTTP 方法", choices=HttpMethod.choices, initial=HttpMethod.GET, required=False)
    target = forms.CharField(label="目标地址", max_length=255)
    headers = forms.CharField(label="自定义请求头(JSON)", required=False, widget=forms.Textarea(attrs={"rows": 4}))
    request_payload = forms.CharField(label="请求体/发包内容", required=False, widget=forms.Textarea(attrs={"rows": 8}))

