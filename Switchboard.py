import asyncio

from Node import Node

from Connection import LoopConnection
from Stream import LoopStream


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

# 0 - Loopback
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
    def __init__(self):
        self.server = None
        self.inboundStreams = []
        self.data = asyncio.Queue()
        self.nodes = [Node.as_loopback(0), Node.as_net_node()]
        self.connections = []

    async def start(self):
        print("Starting server...")
        self.server = await asyncio.start_server(
            self.accept_connection, '127.0.0.1', 8888)
        async with self.server:
            await self.server.serve_forever()

    def accept_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        sock = writer.get_extra_info('socket')
        #Need to know what node to connect to
        if sock:
            sock_info = sock.getpeername()
            self.connections.append(LoopConnection(0, sock_info[0], sock_info[1]))
            self.connections[-1]
            #print(sock.getsockopt('peername'))
        #self.connections.append(LoopConnection())

    async def init_loopback(self):
        print("Initializing loopback node...")
        await self.nodes[0].connect()
