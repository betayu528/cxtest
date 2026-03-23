from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from .forms import PlatformAuthenticationForm, UserProfileForm
from .models import User


class UserListView(ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    queryset = User.objects.order_by("role", "username")


class PlatformLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = PlatformAuthenticationForm
    redirect_authenticated_user = True


class PlatformLogoutView(LogoutView):
    next_page = reverse_lazy("dashboard")


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user
