import asyncio
from Stream import LoopStream


class Switchboard:
    def __init__(self):
        self.server = None
        self.inboundStreams = []
        self.data = asyncio.Queue()
        self.connections = []

    async def start(self):
        self.server = await asyncio.start_server(
            self.accept_connection, '127.0.0.1', 8888)
        async with self.server:
            await self.server.serve_forever()

    async def accept_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        sock = writer.get_extra_info('socket')
        if sock not None:
            print(sock.getsockopt('peername'))
        self.connections.append(LoopConnection())
