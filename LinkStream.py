import asyncio


class LinkStream:
    def __init__(self, parent_link, reader=None, writer=None, is_inbound=True):
        self.parentLink = parent_link
        self.reader = reader
        self.writer = writer
        self.isInbound = is_inbound
        self.buffer = asyncio.Queue()
        self.active = False

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()
        self.active = False

    async def send(self, message):
        await self.buffer.put(message)

    async def process_stream(self):
        if self.isInbound:
            async for line in self.reader:
                print("Msg received...")
                await Message(line, self).deliver()
        else:
            while True:
                message = await self.parentLink.buffer.get()
                self.writer.write(message.encode())
                await self.writer.drain()

    def open(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.active = True
        self.parentLink.parentNode.taskgroup.create_task(self.process_stream())
