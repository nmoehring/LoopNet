
class Message:
    def __init__(self, data, stream):
        self.stream = stream
        self.link = stream.parentLink
        self.node = self.link.parentNode

        self.data = data
        self.delimiter = ":"
        if type(data) is list:
            self.msg = (self.delimiter.join(
                    [(str(item) if type(item) is not str else item) for item in data]))
        elif type(data) is str:
            self.msg = data.decode()
            self.data = self.msg.split(self.delimiter)
        else:
            raise TypeError("Message initializer received unsupported data type.")

    @classmethod
    def from_node(cls, data, node, link_idx, outbound=True):
        return cls(data, node.links[link_idx][1 if outbound else 0].stream)

    async def deliver(self):
        await self.node.inbox.put(self)

    async def send(self):
        self.stream.writer.write(self.msg.encode())
        await self.stream.writer.drain()
