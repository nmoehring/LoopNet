import asyncio

from Message import Message


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
        await self.parentLink.buffer.put(Message(msg, self))

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
