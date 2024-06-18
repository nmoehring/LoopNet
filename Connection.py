import asyncio
from Stream import LoopStream


class LoopConnection:
    def __init__(self, node_id, ip, port, waiting=False):
        self.node_id = node_id
        self.ip = ip
        self.port = port
        self.stream = None
        self.waiting = waiting

    @classmethod
    def as_loopback(cls):
        return cls(0, "127.0.0.1", 8888)

    @classmethod
    def as_net_connection(cls):
        return cls(1, '127.0.0.1', 8888, True)

    def update(self, client_id=None, ip=None, port=None, waiting=None):
        # None argument means no change to that attribute
        self.node_id = client_id if client_id else self.node_id
        self.ip = ip if ip else self.ip
        self.port = port if port else self.port
        self.waiting = waiting if waiting else self.waiting
        return self

    async def open(self):
        reader, writer = await asyncio.open_connection(
            self.ip, self.port)
        self.stream = LoopStream(reader, writer, inbound=False)

    async def close(self):
        self.stream.close()

    async def send(self, message):
        await self.stream.send(message)
