import asyncio


class LoopStream:
    def __init__(self, reader=None, writer=None, inbound=True):
        self.reader = reader
        self.writer = writer
        self.isInbound = inbound
        self.buffer = asyncio.Queue()

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

    async def send(self, message):
        await self.buffer.put(message)

    async def process_stream(self):
        if self.isInbound:
            async for line in self.reader:
                await self.buffer.put(line)
        else:
            while True:
                message = await self.buffer.get()
                self.writer.write(message.encode())
                await self.writer.drain()
