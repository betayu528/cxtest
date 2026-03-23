from django.core.management.base import BaseCommand

from mockserver.models import ProtocolType
from mockserver.runtime import MockRuntimeManager


class Command(BaseCommand):
    help = "启动 TCP / UDP / WebSocket Mock 运行器"

    def add_arguments(self, parser):
        parser.add_argument(
            "--protocol",
            choices=[ProtocolType.TCP, ProtocolType.UDP, ProtocolType.WEBSOCKET, "ALL"],
            default="ALL",
            help="仅启动指定协议",
        )

    def handle(self, *args, **options):
        selected = options["protocol"]
        protocols = None if selected == "ALL" else [selected]
        manager = MockRuntimeManager()
        threads = manager.start(protocols=protocols)
        if not threads:
            self.stdout.write(self.style.WARNING("没有可启动的非 HTTP Mock 服务"))
            return

        for name, protocol, host, port, _thread in threads:
            self.stdout.write(self.style.SUCCESS(f"{protocol} Mock 已启动: {name} @ {host}:{port}"))
        manager.join()
