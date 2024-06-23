import asyncio

from MetaLink import MetaLink
from Node import Node, NodeType
from lingo import NT


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
# Message travels around to

class Switchboard:
    def __init__(self, taskgroup):
        self.server = None
        self.inboundStreams = []
        self.data = asyncio.Queue()
        self.invites = asyncio.Queue()
        self.expectedConnects = []
        self.nodes = [Node.as_loopback(taskgroup, self.invites), Node(taskgroup, self.invites)]
        self.initNode = Node(taskgroup, -1, node_type=NT.INIT)
        self.connectBuffer = []
        self.taskgroup = taskgroup

    async def start(self):
        print("Starting server...")
        self.server = await asyncio.start_server(
            self.accept_connection, '127.0.0.1', 8888)
        async with self.server:
            await self.server.serve_forever()

    async def process_queues(self):
        self.taskgroup.create_task(self.get_invites())

    async def get_invites(self):
        while True:
            self.expectedConnects.append(await self.invites.get())

    def accept_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        info = MetaLink.from_streams(reader, writer)
        #Need to know what node to connect to
        #connect() just suppposed to advertise intent to connect
        #a new node is inserted when the loop node connects to the server of the new node,
        # then the oNode assignment for the new node and the iNode assignment for the next
        # node in the loop are directed by the insertion node
        self.connectBuffer.append(info)
        print(info.addr, ":", info.port, "connected.")
            #print(sock.getsockopt('peername'))
        #self.connections.append(NodeLink())

    def fill_invites(self):
        filled = []
        for idx1 in range(len(self.expectedConnects)):
            for idx2 in range(len(self.connectBuffer)):
                if self.expectedConnects[idx1] == self.connectBuffer[idx2]:
                    filled.append((idx1, idx2))
        for idx in filled:
            self.expectedConnects[idx[0]].updateNode(self.connectBuffer[idx[1]])
        done_expected = sorted([f[0] for f in filled], reverse=True)
        done_connected = sorted([f[1] for f in filled], reverse=True)
        for idx in range(len(filled)):
            del self.expectedConnects[done_expected[idx]]
            del self.connectBuffer[done_expected[idx]]

    async def init_loopback(self):
        print("Initializing loopback node...")
        await self.nodes[0].init_connect()
