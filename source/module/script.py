from contextlib import suppress
from json import loads
from websockets import ConnectionClosed, serve
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..application import XHS


class ScriptServer:
    def __init__(
        self,
        core: "XHS",
        host="127.0.0.1",
        port=5558,
    ):
        self.core = core
        self.host = host
        self.port = port
        self.server = None

    async def handler(self, websocket):
        with suppress(ConnectionClosed):
            async for message in websocket:
                payload = loads(message)
                data = payload.get("data")
                index = payload.get("index")
                if data is not None:
                    await self.core.deal_script_tasks(data, index)

    async def start(self):
        """启动服务器"""
        self.server = await serve(
            self.handler,
            self.host,
            self.port,
        )

    async def stop(self):
        """停止服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
