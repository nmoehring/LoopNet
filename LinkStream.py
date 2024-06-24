import asyncio

from Mail import Mail


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
        self.reader = None
        self.writer = None
        while not self.parentLink.buffer.empty():
            await self.parentLink.buffer.get()

    async def send(self, msg):
        await self.parentLink.buffer.put(Mail(msg, self))

    async def read_stream(self):
        while True:
            async for line in self.reader:
                print("Msg received...")
                await Mail(line, self).deliver()

    def open(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.active = True
        if self.isInbound:
            self.parentLink.parentNode.taskgroup.create_task(self.read_stream())
