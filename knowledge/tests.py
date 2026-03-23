from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import User, UserRole
from knowledge.models import Article, ArticleFavorite, ArticleLike


class KnowledgeFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="author", password="pass123456", role=UserRole.TEST)
        self.article = Article.objects.create(title="Markdown Demo", content="# hello", author=self.user)

    def test_article_detail_is_reachable(self):
        response = self.client.get(reverse("knowledge:article-detail", kwargs={"pk": self.article.id}))
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_comment_like_and_favorite(self):
        self.client.login(username="author", password="pass123456")
        comment_response = self.client.post(
            reverse("knowledge:article-comment", kwargs={"pk": self.article.id}),
            {"content": "nice article"},
        )
        like_response = self.client.post(reverse("knowledge:article-react", kwargs={"pk": self.article.id, "action": "like"}))
        favorite_response = self.client.post(
            reverse("knowledge:article-react", kwargs={"pk": self.article.id, "action": "favorite"})
        )
        self.article.refresh_from_db()
        self.assertEqual(comment_response.status_code, 302)
        self.assertEqual(like_response.status_code, 302)
        self.assertEqual(favorite_response.status_code, 302)
        self.assertEqual(self.article.comments.count(), 1)
        self.assertEqual(ArticleLike.objects.filter(article=self.article, user=self.user).count(), 1)
        self.assertEqual(ArticleFavorite.objects.filter(article=self.article, user=self.user).count(), 1)

    def test_authenticated_user_can_create_article(self):
        self.client.login(username="author", password="pass123456")
        response = self.client.post(
            reverse("knowledge:article-create"),
            {
                "title": "New Article",
                "summary": "summary",
                "content_format": "MARKDOWN",
                "content": "## body",
                "is_published": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Article.objects.filter(title="New Article", author=self.user).exists())
