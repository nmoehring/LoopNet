import asyncio

from MetaLink import MetaLink
from Node import Node, NodeType
from lingo import NT, LM, NS, NodeState, LT, LD


class Switchboard:
    def __init__(self, taskgroup):
        self.server = None
        self.invites = asyncio.Queue()
        self.expectedConnects = []
        self.connectBuffer = []
        self.inbox = asyncio.Queue()
        self.outbox = asyncio.Queue()
        self.nodes = [Node.as_loopback(taskgroup, self.invites, self.inbox, self.outbox),
                      Node(taskgroup, self.invites, self.inbox, self.outbox)]
        self.initNode = Node(taskgroup, self.invites, self.inbox, self.outbox,
                             node_id=1, node_type=NT.INIT)
        self.taskgroup = taskgroup

    async def start(self):
        print("Starting async queue handlers...")
        await self.process_queues()

        print("Starting server...")
        self.server = await asyncio.start_server(
            self.accept_connection, '127.0.0.1', 8888)
        async with self.server:
            await self.server.serve_forever()

    async def process_queues(self):
        self.taskgroup.create_task(self.get_invites())
        self.taskgroup.create_task(self.check_mail())
        self.taskgroup.create_task(self.send_mail())
        self.taskgroup.create_task(self.write_streams())

    async def get_invites(self):
        while True:
            self.expectedConnects.append(await self.invites.get())

    async def check_mail(self):
        while True:
            await self.parse_mail(await self.inbox.get())

    async def send_mail(self):
        while True:
            await (await self.outbox.get()).send()

    async def write_streams(self):
        while True:
            mail = await self.outbox.get()
            mail.stream.writer.write(mail.msg.encode())
            await mail.stream.writer.drain()

    async def parse_mail(self, mail):
        data = mail.data
        node = mail.node
        link = mail.link
        if node == self and data[0] != LM.INSERT_FINAL_DATA:
            raise TypeError("A MetaLink sent the wrong message.")
        match data[0]:
            case LM.NEW_CONNECT:
                await node.begin_insert(data[1], data[2], data[3])
            case LM.INSERT_EXPECT:
                await node.invites.put(data[1:])
                node.status = NS.WAIT_NEW_IB
            case LM.INSERT_CONNECT_OB:
                node.update_link(data[1], data[2], data[3], LT.TEMP, LD.OUT)
                node.links[LT.TEMP][LD.OUT].open()
                node.send_msg(LM.INSERT_FINAL_DATA, LT.TEMP)
                node.status = NS.INSERT_WAIT_CLOSE
            case LM.INSERT_FINAL_DATA:
                link.hostNodeId = data[1]
            case LM.INSERT_LOOP_CLOSED:
                if node.status in (NodeState.WAIT_INSERTION, NodeState.WAIT_2LOOP):
                    await node.finish_insert()

    def accept_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        info = MetaLink.from_streams(reader, writer, self)
        self.connectBuffer.append(info)
        print(info.clientAddr, ":", info.clientPort, "connected.")
            #print(sock.getsockopt('peername'))
        #self.connections.append(NodeLink())

    def fill_invites(self):
        filled = []
        for idx1 in range(len(self.expectedConnects)):
            for idx2 in range(len(self.connectBuffer)):
                if self.expectedConnects[idx1] == self.connectBuffer[idx2]:
                    filled.append((idx1, idx2))
        for idx in filled:
            self.expectedConnects[idx[0]].prepare_node_update(self.connectBuffer[idx[1]])
        done_expected = sorted([f[0] for f in filled], reverse=True)
        done_connected = sorted([f[1] for f in filled], reverse=True)
        for idx in range(len(filled)):
            del self.expectedConnects[done_expected[idx]]
            del self.connectBuffer[done_connected[idx]]

    async def init_loopback(self):
        print("Initializing loopback node...")
        await self.nodes[0].init_connect()
