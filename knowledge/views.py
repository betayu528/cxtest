from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from .forms import ArticleCommentForm, ArticleForm
from .models import Article, ArticleFavorite, ArticleLike


class ArticleListView(ListView):
    model = Article
    template_name = "knowledge/article_list.html"
    context_object_name = "articles"
    queryset = (
        Article.objects.select_related("project", "author")
        .prefetch_related("comments", "likes", "favorites")
        .annotate(comment_count=Count("comments"))
        .order_by("-is_recommended", "-heat", "-published_at")
    )


class ArticleDetailView(DetailView):
    model = Article
    template_name = "knowledge/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.select_related("project", "author").prefetch_related("comments__author", "likes", "favorites")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        user = self.request.user
        context["comment_form"] = ArticleCommentForm()
        context["liked"] = user.is_authenticated and article.likes.filter(user=user).exists()
        context["favorited"] = user.is_authenticated and article.favorites.filter(user=user).exists()
        return context


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "knowledge/article_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "文章已发布")
        return response

    def get_success_url(self):
        return reverse("knowledge:article-detail", kwargs={"pk": self.object.pk})


class ArticleCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        form = ArticleCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            article.heat += 2
            article.save(update_fields=["heat"])
        return HttpResponseRedirect(reverse("knowledge:article-detail", kwargs={"pk": pk}))


class ArticleReactView(LoginRequiredMixin, View):
    def post(self, request, pk, action):
        article = get_object_or_404(Article, pk=pk)
        if action == "like":
            like, created = ArticleLike.objects.get_or_create(article=article, user=request.user)
            if not created:
                like.delete()
            else:
                article.heat += 1
                article.save(update_fields=["heat"])
        elif action == "favorite":
            favorite, created = ArticleFavorite.objects.get_or_create(article=article, user=request.user)
            if not created:
                favorite.delete()
            else:
                article.heat += 1
                article.save(update_fields=["heat"])
        elif action == "share":
            article.share_count += 1
            article.heat += 1
            article.save(update_fields=["share_count", "heat"])
        return HttpResponseRedirect(reverse("knowledge:article-detail", kwargs={"pk": pk}))
