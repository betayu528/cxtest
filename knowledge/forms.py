from django import forms

from .models import Article, ArticleComment


class ArticleForm(forms.ModelForm):
    rich_content = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Article
        fields = ["project", "title", "summary", "content_format", "content", "is_published"]
        widgets = {
            "summary": forms.TextInput(attrs={"placeholder": "一句话摘要，展示在列表页"}),
            "content": forms.Textarea(attrs={"rows": 18, "id": "id_content_editor"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("content_format") == "RICHTEXT" and self.data.get("rich_content"):
            cleaned["content"] = self.data.get("rich_content")
        return cleaned


class ArticleCommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "placeholder": "写下你的评论"}),
        }
