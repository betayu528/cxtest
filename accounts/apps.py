from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        from django.contrib.auth.models import Group, Permission
        from django.db.models.signals import post_migrate, post_save
        from django.dispatch import receiver

        from .models import User, UserRole

        role_group_map = {
            UserRole.TEST: "测试",
            UserRole.DEV: "开发",
            UserRole.PRODUCT: "产品",
            UserRole.OPS: "运营",
            UserRole.ADMIN: "管理员",
        }

        role_permissions = {
            "测试": {
                "projects": {"view"},
                "cases": {"view", "add", "change"},
                "api_testing": {"view", "add", "change"},
                "async_tasks": {"view", "add", "change"},
                "mockserver": {"view", "add", "change"},
                "datahub": {"view", "add", "change"},
                "bugs": {"view", "add", "change"},
                "knowledge": {"view", "add", "change"},
                "notifications": {"view"},
            },
            "开发": {
                "projects": {"view", "change"},
                "cases": {"view", "change"},
                "api_testing": {"view", "change"},
                "async_tasks": {"view", "add", "change"},
                "mockserver": {"view", "add", "change"},
                "datahub": {"view", "change"},
                "bugs": {"view", "add", "change"},
                "knowledge": {"view", "add", "change"},
                "notifications": {"view"},
            },
            "产品": {
                "projects": {"view"},
                "cases": {"view", "add", "change"},
                "bugs": {"view", "add", "change"},
                "knowledge": {"view", "add", "change"},
                "notifications": {"view"},
            },
            "运营": {
                "projects": {"view"},
                "async_tasks": {"view", "add", "change"},
                "mockserver": {"view", "add", "change"},
                "datahub": {"view", "add", "change"},
                "knowledge": {"view", "add", "change"},
                "notifications": {"view", "add", "change"},
            },
        }

        @receiver(post_migrate, dispatch_uid="accounts_init_role_groups")
        def init_role_groups(sender, **kwargs):
            if sender.name != self.name:
                return

            all_permissions = Permission.objects.all()
            for group_name in role_group_map.values():
                group, _ = Group.objects.get_or_create(name=group_name)
                if group_name == "管理员":
                    group.permissions.set(all_permissions)
                    continue

                selected_ids = []
                app_map = role_permissions.get(group_name, {})
                for permission in all_permissions:
                    actions = app_map.get(permission.content_type.app_label)
                    if not actions:
                        continue
                    if permission.codename.split("_", 1)[0] in actions:
                        selected_ids.append(permission.id)
                group.permissions.set(selected_ids)

        @receiver(post_save, sender=User, dispatch_uid="accounts_sync_user_group")
        def sync_user_group(sender, instance, **kwargs):
            group_name = role_group_map.get(instance.role)
            if not group_name or not instance.pk:
                return
            group = Group.objects.filter(name=group_name).first()
            if group is None:
                return
            instance.groups.set([group])
