import asyncio
from LinkStream import LinkStream
from vocab import LD


class NodeLink:
    def __init__(self, parent_node, link_type, link_dir):
        self.parentNode = parent_node
        self.otherNodeId = 1
        self.linkType = link_type
        self.linkDir = link_dir
        self.ip = '127.0.0.1'
        self.port = 8888
        self.stream = LinkStream(self)
        self.waiting = True if self.linkDir == LD.IN else False

    @classmethod
    def as_pair(cls, parent_node, link_type):
        return (cls(parent_node, link_type, LD.IN),
                cls(parent_node, link_type, LD.OUT))

    def is_loopback(self):
        return self.parentNode.nodeId == 0

    def get_info(self):
        return [self.ip, self.port, self.otherNodeId]

    def update(self, node_id, ip=None, port=None):
        # None argument means no change to that attribute
        self.ip = ip if ip else self.ip
        self.port = port if port else self.port
        self.otherNodeId = node_id
        return self

    async def reset(self):
        self.ip = '127.0.0.1'
        self.port = 8888
        self.otherNodeId = 1
        await self.stream.reset()

    async def open(self):
        reader, writer = await asyncio.open_connection(
            self.ip, self.port)
        self.stream = LinkStream(reader, writer, False)

    async def close(self):
        await self.stream.close()

    async def send(self, message):
        await self.stream.send(message)
