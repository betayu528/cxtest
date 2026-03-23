from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class PlatformAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="用户名")
    password = forms.CharField(label="密码", widget=forms.PasswordInput)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["display_name", "email", "mobile", "title", "bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
