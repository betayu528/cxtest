from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    TEST = "TEST", "测试"
    DEV = "DEV", "开发"
    PRODUCT = "PRODUCT", "产品"
    OPS = "OPS", "运营"
    ADMIN = "ADMIN", "管理员"


class User(AbstractUser):
    role = models.CharField("角色", max_length=20, choices=UserRole.choices, default=UserRole.TEST)
    display_name = models.CharField("显示名称", max_length=64, blank=True)
    mobile = models.CharField("手机号", max_length=20, blank=True)
    title = models.CharField("岗位", max_length=64, blank=True)
    avatar = models.ImageField("头像", upload_to="avatars/", blank=True)
    bio = models.TextField("个人简介", blank=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.display_name or self.username
