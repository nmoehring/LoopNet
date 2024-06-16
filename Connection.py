import asyncio
from Stream import LoopStream


class LoopConnection:
    def __init__(self, client_id, ip, port):
        self.clientId = client_id
        self.ip = ip
        self.port = port
        self.stream = None

    @classmethod
    def as_loopback(cls, client_id):
        return cls(client_id, "127.0.0.1", 80)

    def update(self, client_id=None, ip=None, port=None):
        # None argument means no change to that attribute
        self.clientId = client_id if client_id else self.clientId
        self.ip = ip if ip else self.ip
        self.port = port if port else self.port
        return self

    async def open(self):
        reader, writer = await asyncio.open_connection(
            self.ip, self.port)
        self.stream = LoopStream(reader, writer, inbound=False)

    async def close(self):
        self.stream.close()

    async def send(self, message):
        await self.stream.send(message)

#
#   async def receive(self, data):
#       data = await self.reader.read(100)
#       print(f'Received: {data.decode()!r}')
