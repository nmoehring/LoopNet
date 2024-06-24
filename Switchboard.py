import asyncio

from MetaLink import MetaLink
from Node import Node, NodeType
from lingo import NT, LM, NS, NodeState, LT, LD


# Loops are connected nodes, nodes send data one way (need to figure out how to prevent
#   data going the wrong direction on sockets)
# Knots are 2 loops tied together, one going the opposite direction
#   4 Loops are tied together into 4 knots, so each node belongs to 2 knots
# The complete 4 loops in 4 knots is a toroid, and I guess will be considered the most
#   fundamental stable unit of the LoopNet
# There are many paths through the toroid, so the toroid may be the most capable
#   small-scale structure to handle loop breakages or other issues, or maybe just
#   the largest identifiable structure

# The most complete toroid possible forms from the beginning
# The first 4 nodes should be in separate loops, laced together
# Once stack is established, stacks split
# Stack-stacks form, with different node columns representing at different layers
#

# 0 - LOOPBACK
# 1 - Connection Loop And Stack - Connect to everything everywhere as good as possible
#                               - Higher

# Connecting node:
#      Accept
# Insertion node sends message forward:
#      "expect new connection from the new node address"
# Insertion
# New node connects to their new output node
# New node sends message through new loop which contains their address
# Mail travels around to

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
        self.initNode = Node(taskgroup, -1, node_type=NT.INIT)
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
        #Need to know what node to connect to
        #connect() just suppposed to advertise intent to connect
        #a new node is inserted when the loop node connects to the server of the new node,
        # then the oNode assignment for the new node and the iNode assignment for the next
        # node in the loop are directed by the insertion node
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
