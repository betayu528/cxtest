import secrets

from django.core.management.base import BaseCommand

from accounts.models import User, UserRole
from api_testing.models import ApiCollection, ApiEndpoint
from async_tasks.models import AsyncTaskExecution, CIIntegration, CIProvider, TaskSource, TaskStatus, TaskType
from bugs.models import BugComment, BugPost
from cases.models import CaseSource, CaseType, TestCase
from datahub.models import TestDataRecord, TestDataset
from knowledge.models import Article, ArticleComment
from mockserver.models import MockRule, MockService, ProtocolType
from notifications.models import Notification
from projects.models import Environment, Project


class Command(BaseCommand):
    help = "初始化测试平台演示数据"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            username="admin_demo",
            defaults={"role": UserRole.ADMIN, "is_staff": True, "is_superuser": True, "display_name": "管理员"},
        )
        admin.set_password("admin123456")
        admin.save()

        tester, _ = User.objects.get_or_create(
            username="tester_demo",
            defaults={"role": UserRole.TEST, "display_name": "测试同学"},
        )
        tester.set_password("tester123456")
        tester.save()

        project, _ = Project.objects.get_or_create(
            code="TP-DEMO",
            defaults={
                "name": "测试平台演示项目",
                "description": "演示测试平台核心能力",
                "owner": tester,
                "repo_url": "https://git.example.com/demo/test-platform.git",
            },
        )
        project.members.add(admin, tester)
        Environment.objects.get_or_create(project=project, name="测试环境", defaults={"base_url": "https://api.demo.local"})
        subproject, _ = Project.objects.get_or_create(
            code="TP-DEMO-WEB",
            defaults={
                "name": "Web 端回归",
                "description": "演示用例子项目",
                "owner": tester,
                "parent": project,
            },
        )

        case, _ = TestCase.objects.get_or_create(
            project=subproject,
            case_id="CASE-001",
            defaults={
                "name": "登录接口返回成功",
                "owner": tester,
                "description": "验证账号密码登录流程",
                "expected_result": "返回 200 和 token",
                "precondition": "测试账号已创建",
                "execution_env": "测试环境",
                "case_type": CaseType.AUTOMATED,
                "source": CaseSource.POSTMAN,
                "repo_url": project.repo_url,
            },
        )
        TestCase.objects.get_or_create(
            project=subproject,
            case_id="CASE-002",
            defaults={
                "name": "首页核心模块展示",
                "owner": tester,
                "description": "验证首页展示项目、任务、知识模块",
                "expected_result": "页面元素正常显示",
                "precondition": "已登录系统",
                "execution_env": "Web 测试环境",
                "case_type": CaseType.MANUAL,
                "source": CaseSource.NATIVE,
            },
        )

        collection, _ = ApiCollection.objects.get_or_create(
            project=project,
            name="用户中心 API",
            defaults={"created_by": tester, "raw_payload": {"info": {"name": "用户中心 API"}}},
        )
        ApiEndpoint.objects.get_or_create(
            collection=collection,
            name="登录",
            defaults={"method": "POST", "path": "/api/login", "request_body": {"username": "demo"}},
        )

        jenkins_integration, _ = CIIntegration.objects.get_or_create(
            project=project,
            name="Jenkins 冒烟流水线",
            defaults={
                "provider": CIProvider.JENKINS,
                "base_url": "https://jenkins.example.com",
                "callback_base_url": "http://127.0.0.1:8000",
                "jenkins_job_name": "demo-smoke",
                "jenkins_token": "replace-me",
                "default_payload": {"env": "test"},
            },
        )
        gitlab_integration, _ = CIIntegration.objects.get_or_create(
            project=project,
            name="GitLab 回归流水线",
            defaults={
                "provider": CIProvider.GITLAB_CI,
                "base_url": "https://gitlab.example.com",
                "callback_base_url": "http://127.0.0.1:8000",
                "gitlab_project_id": "123",
                "gitlab_trigger_token": "replace-me",
                "gitlab_ref": "main",
                "default_payload": {"suite": "regression"},
            },
        )

        task, _ = AsyncTaskExecution.objects.get_or_create(
            callback_token="demo-callback-token",
            defaults={
                "project": project,
                "integration": jenkins_integration,
                "task_type": TaskType.SUITE_RUN,
                "source": TaskSource.JENKINS,
                "status": TaskStatus.RUNNING,
                "title": "演示用例集执行",
                "description": f"执行 {case.case_id}",
                "external_job_name": "demo-pipeline",
                "external_build_id": "build-001",
                "created_by": tester,
                "payload": {"suite": "smoke"},
            },
        )
        AsyncTaskExecution.objects.get_or_create(
            callback_token="demo-pending-token",
            defaults={
                "project": project,
                "integration": gitlab_integration,
                "task_type": TaskType.API_RUN,
                "source": TaskSource.PLATFORM,
                "status": TaskStatus.PENDING,
                "title": "待执行 API 回归",
                "description": "演示开始按钮",
                "created_by": tester,
                "payload": {"suite": "api"},
            },
        )
        AsyncTaskExecution.objects.get_or_create(
            callback_token="demo-failed-token",
            defaults={
                "project": project,
                "integration": gitlab_integration,
                "task_type": TaskType.ENV_DEPLOY,
                "source": TaskSource.GITLAB_CI,
                "status": TaskStatus.FAILED,
                "title": "失败的部署任务",
                "description": "演示重试按钮",
                "created_by": tester,
                "result": {"error": "deploy failed"},
            },
        )

        service, _ = MockService.objects.get_or_create(
            project=project,
            name="登录 HTTP Mock",
            protocol=ProtocolType.HTTP,
            route="/demo/login",
            defaults={"port": 8001},
        )
        MockRule.objects.get_or_create(
            service=service,
            name="默认登录成功",
            defaults={"response_body": {"code": 0, "message": "success", "token": secrets.token_hex(8)}},
        )
        tcp_service, _ = MockService.objects.get_or_create(
            project=project,
            name="TCP Echo Mock",
            protocol=ProtocolType.TCP,
            port=9101,
            defaults={"config": {"message_format": "text"}},
        )
        MockRule.objects.get_or_create(
            service=tcp_service,
            name="TCP ping-pong",
            defaults={"matcher": {"contains": "ping"}, "response_body": "pong from tcp"},
        )
        udp_service, _ = MockService.objects.get_or_create(
            project=project,
            name="UDP Status Mock",
            protocol=ProtocolType.UDP,
            port=9102,
            defaults={"config": {"message_format": "json"}},
        )
        MockRule.objects.get_or_create(
            service=udp_service,
            name="UDP status",
            defaults={"matcher": {"contains": "status"}, "response_body": {"status": "ok", "source": "udp"}},
        )
        ws_service, _ = MockService.objects.get_or_create(
            project=project,
            name="WebSocket Notify Mock",
            protocol=ProtocolType.WEBSOCKET,
            port=9103,
            defaults={"config": {"message_format": "json"}},
        )
        MockRule.objects.get_or_create(
            service=ws_service,
            name="WebSocket hello",
            defaults={"matcher": {"contains": "hello"}, "response_body": {"message": "hello from websocket"}},
        )

        dataset, _ = TestDataset.objects.get_or_create(
            project=project,
            name="登录测试账号",
            defaults={"description": "登录场景测试数据", "created_by": tester, "tags": ["login", "smoke"]},
        )
        TestDataRecord.objects.get_or_create(dataset=dataset, remark="默认账号", defaults={"data": {"username": "demo", "password": "123456"}})

        post, _ = BugPost.objects.get_or_create(
            title="登录后偶发 500",
            defaults={"project": project, "author": tester, "content": "复盘历史线上问题", "is_pinned": True, "heat": 88},
        )
        BugComment.objects.get_or_create(post=post, content="根因是缓存击穿", defaults={"author": admin})

        article, _ = Article.objects.get_or_create(
            title="如何设计稳定的回归集",
            defaults={
                "project": project,
                "author": tester,
                "summary": "从业务分层、优先级和环境隔离三个维度整理回归集设计方法。",
                "content": "回归集需要围绕高价值链路、稳定环境与反馈速度做设计。",
                "is_recommended": True,
                "heat": 66,
            },
        )
        ArticleComment.objects.get_or_create(article=article, content="这篇可以作为团队规范", defaults={"author": admin})

        Notification.objects.get_or_create(
            user=tester,
            title="演示任务进行中",
            defaults={"content": f"任务 {task.title} 正在执行", "category": "TASK"},
        )
        Notification.objects.get_or_create(
            user=tester,
            title="CI 集成已配置",
            defaults={"content": f"已初始化 {jenkins_integration.name} 和 {gitlab_integration.name}", "category": "SYSTEM"},
        )

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成"))
        self.stdout.write("管理员账号: admin_demo / admin123456")
        self.stdout.write("测试账号: tester_demo / tester123456")
