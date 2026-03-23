import asyncio
import base64
import hashlib
import json
import socket
import struct
import threading
import time
from typing import Any

from django.db import close_old_connections

from .models import MockService, ProtocolType


def normalize_body(body: Any, message_format: str = "text") -> bytes:
    if isinstance(body, bytes):
        return body
    if message_format == "json":
        return json.dumps(body, ensure_ascii=False).encode("utf-8")
    if isinstance(body, (dict, list)):
        return json.dumps(body, ensure_ascii=False).encode("utf-8")
    return str(body).encode("utf-8")


def resolve_rule(rules, incoming_text):
    for rule in rules:
        matcher = rule.matcher or {}
        exact = matcher.get("equals")
        contains = matcher.get("contains")
        if exact is not None and incoming_text != str(exact):
            continue
        if contains is not None and str(contains) not in incoming_text:
            continue
        return rule
    return rules[0] if rules else None


def get_service_snapshot(service_id):
    close_old_connections()
    service = MockService.objects.filter(id=service_id, is_enabled=True).prefetch_related("rules").first()
    if service is None:
        return None
    return {
        "id": service.id,
        "name": service.name,
        "protocol": service.protocol,
        "host": service.host,
        "port": service.port,
        "config": service.config or {},
        "rules": list(service.rules.all()),
    }


class TCPMockServer:
    def __init__(self, service_id):
        self.service_id = service_id

    async def run(self):
        snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
        if snapshot is None:
            return
        server = await asyncio.start_server(
            lambda reader, writer: self.handle_connection(reader, writer),
            snapshot["host"],
            snapshot["port"],
        )
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
        if snapshot is None:
            writer.close()
            await writer.wait_closed()
            return
        data = await reader.read(65535)
        incoming_text = data.decode("utf-8", errors="ignore")
        rule = resolve_rule(snapshot["rules"], incoming_text)
        if rule is None:
            writer.close()
            await writer.wait_closed()
            return
        if rule.response_delay_ms:
            await asyncio.sleep(rule.response_delay_ms / 1000)
        message_format = snapshot["config"].get("message_format", "text")
        writer.write(normalize_body(rule.response_body, message_format))
        await writer.drain()
        writer.close()
        await writer.wait_closed()


class UDPMockServer(asyncio.DatagramProtocol):
    def __init__(self, service_id):
        self.service_id = service_id
        self.transport = None

    async def run(self):
        snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
        if snapshot is None:
            return
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: self,
            local_addr=(snapshot["host"], snapshot["port"]),
        )
        self.transport = transport
        await asyncio.Future()

    def datagram_received(self, data, addr):
        asyncio.create_task(self._respond(data, addr))

    async def _respond(self, data, addr):
        snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
        if snapshot is None or self.transport is None:
            return
        incoming_text = data.decode("utf-8", errors="ignore")
        rule = resolve_rule(snapshot["rules"], incoming_text)
        if rule is None:
            return
        if rule.response_delay_ms:
            await asyncio.sleep(rule.response_delay_ms / 1000)
        message_format = snapshot["config"].get("message_format", "text")
        self.transport.sendto(normalize_body(rule.response_body, message_format), addr)


class WebSocketMockServer:
    GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, service_id):
        self.service_id = service_id

    async def run(self):
        snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
        if snapshot is None:
            return
        server = await asyncio.start_server(
            lambda reader, writer: self.handle_connection(reader, writer),
            snapshot["host"],
            snapshot["port"],
        )
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader, writer):
        request_data = await reader.readuntil(b"\r\n\r\n")
        headers = self._parse_headers(request_data.decode("utf-8", errors="ignore"))
        key = headers.get("sec-websocket-key")
        if not key:
            writer.close()
            await writer.wait_closed()
            return

        accept = base64.b64encode(hashlib.sha1((key + self.GUID).encode("utf-8")).digest()).decode("ascii")
        response = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
        )
        writer.write(response.encode("utf-8"))
        await writer.drain()

        while True:
            frame = await self._read_frame(reader)
            if frame is None:
                break
            opcode, payload = frame
            if opcode == 0x8:
                break
            if opcode == 0x9:
                writer.write(self._build_frame(payload, opcode=0xA))
                await writer.drain()
                continue

            incoming_text = payload.decode("utf-8", errors="ignore")
            snapshot = await asyncio.to_thread(get_service_snapshot, self.service_id)
            if snapshot is None:
                break
            rule = resolve_rule(snapshot["rules"], incoming_text)
            if rule is None:
                continue
            if rule.response_delay_ms:
                await asyncio.sleep(rule.response_delay_ms / 1000)
            message_format = snapshot["config"].get("message_format", "text")
            writer.write(self._build_frame(normalize_body(rule.response_body, message_format), opcode=0x1))
            await writer.drain()

        writer.close()
        await writer.wait_closed()

    def _parse_headers(self, raw_request):
        lines = raw_request.split("\r\n")
        headers = {}
        for line in lines[1:]:
            if ": " not in line:
                continue
            key, value = line.split(": ", 1)
            headers[key.lower()] = value.strip()
        return headers

    async def _read_frame(self, reader):
        header = await reader.readexactly(2)
        first_byte, second_byte = header[0], header[1]
        opcode = first_byte & 0x0F
        masked = (second_byte >> 7) & 1
        payload_len = second_byte & 0x7F
        if payload_len == 126:
            payload_len = struct.unpack("!H", await reader.readexactly(2))[0]
        elif payload_len == 127:
            payload_len = struct.unpack("!Q", await reader.readexactly(8))[0]
        masking_key = await reader.readexactly(4) if masked else b""
        payload = await reader.readexactly(payload_len)
        if masked:
            payload = bytes(byte ^ masking_key[i % 4] for i, byte in enumerate(payload))
        return opcode, payload

    def _build_frame(self, payload, opcode=0x1):
        payload_len = len(payload)
        header = bytearray([0x80 | opcode])
        if payload_len < 126:
            header.append(payload_len)
        elif payload_len < 65536:
            header.append(126)
            header.extend(struct.pack("!H", payload_len))
        else:
            header.append(127)
            header.extend(struct.pack("!Q", payload_len))
        return bytes(header) + payload


class MockRuntimeManager:
    def __init__(self):
        self.threads = []

    def load_services(self, protocols=None):
        close_old_connections()
        queryset = MockService.objects.filter(is_enabled=True)
        if protocols:
            queryset = queryset.filter(protocol__in=protocols)
        return list(queryset.values_list("id", "protocol", "name", "host", "port"))

    def start(self, protocols=None):
        services = self.load_services(protocols)
        for service_id, protocol, name, host, port in services:
            if protocol == ProtocolType.HTTP:
                continue
            target = self._target_for_protocol(protocol)
            if target is None:
                continue
            thread = threading.Thread(target=self._run_async_server, args=(target(service_id),), daemon=True, name=f"mock-{name}-{port}")
            thread.start()
            self.threads.append((name, protocol, host, port, thread))
        return self.threads

    def _target_for_protocol(self, protocol):
        mapping = {
            ProtocolType.TCP: TCPMockServer,
            ProtocolType.UDP: UDPMockServer,
            ProtocolType.WEBSOCKET: WebSocketMockServer,
        }
        return mapping.get(protocol)

    def _run_async_server(self, server):
        asyncio.run(server.run())

    def join(self):
        while True:
            time.sleep(1)
