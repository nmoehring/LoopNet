import asyncio
from LinkStream import LinkStream


class NodeLink:
    def __init__(self, parent_node, ip, port, idx1, idx2,
                 other_node_id=1, is_inbound=True):
        self.parentNode = parent_node
        self.otherNodeId = other_node_id
        self.idx = (idx1, idx2)
        self.ip = ip
        self.port = port
        self.stream = LinkStream(self)
        self.waiting = True if is_inbound else False

    @classmethod
    def as_loopback(cls, parent_node, idx1, idx2, is_inbound=True):
        return cls(parent_node, "127.0.0.1", 8888, idx1, idx2, is_inbound)

    @classmethod
    def as_netlink(cls, parent_node, idx1, idx2, is_inbound=True):
        return cls(parent_node, '127.0.0.1', 8888, idx1, idx2, is_inbound)

    @classmethod
    def as_loopback_pair(cls, parent_node, idx):
        return (cls.as_loopback(parent_node, idx, 0, True),
                cls.as_loopback(parent_node, idx, 1, False))

    @classmethod
    def as_netlink_pair(cls, parent_node, idx):
        return (cls.as_netlink(parent_node, idx, 0, True),
                cls.as_netlink(parent_node, idx, 1, False))

    def is_loopback(self):
        return self.parentNode.node_id == 0

    def update(self, ip=None, port=None):
        # None argument means no change to that attribute
        self.ip = ip if ip else self.ip
        self.port = port if port else self.port
        return self

    async def open(self):
        reader, writer = await asyncio.open_connection(
            self.ip, self.port)
        self.stream = LinkStream(reader, writer, False)

    async def close(self):
        await self.stream.close()

    async def send(self, message):
        await self.stream.send(message)
