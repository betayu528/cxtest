from django.urls import path

from .views import PlatformLoginView, PlatformLogoutView, ProfileView, UserListView

app_name = "accounts"

urlpatterns = [
    path("login/", PlatformLoginView.as_view(), name="login"),
    path("logout/", PlatformLogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", UserListView.as_view(), name="user-list"),
]
