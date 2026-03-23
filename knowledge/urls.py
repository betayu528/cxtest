from django.urls import path

from .views import ArticleCommentCreateView, ArticleCreateView, ArticleDetailView, ArticleListView, ArticleReactView

app_name = "knowledge"

urlpatterns = [
    path("", ArticleListView.as_view(), name="article-list"),
    path("create/", ArticleCreateView.as_view(), name="article-create"),
    path("<int:pk>/", ArticleDetailView.as_view(), name="article-detail"),
    path("<int:pk>/comment/", ArticleCommentCreateView.as_view(), name="article-comment"),
    path("<int:pk>/react/<str:action>/", ArticleReactView.as_view(), name="article-react"),
]
