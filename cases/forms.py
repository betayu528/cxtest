from django import forms

from projects.models import Project

from .models import CaseSource, ProjectDocument, TestCase


class SubProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "code", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = [
            "case_id",
            "name",
            "owner",
            "description",
            "expected_result",
            "precondition",
            "execution_env",
            "priority",
            "case_type",
            "source",
            "repo_url",
            "pytest_node",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "expected_result": forms.Textarea(attrs={"rows": 3}),
            "precondition": forms.Textarea(attrs={"rows": 3}),
        }


class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["title", "source", "file"]

    def clean_source(self):
        source = self.cleaned_data["source"]
        if source not in {CaseSource.PDF, CaseSource.EXCEL, CaseSource.XMIND}:
            raise forms.ValidationError("仅支持 PDF / Excel / XMind 文件")
        return source
