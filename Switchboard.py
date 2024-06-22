import asyncio

from Node import Node, NodeType
from vocab import NT


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
        self.nodes = [Node.as_loopback(taskgroup), Node(taskgroup)]
        self.initNode = Node(taskgroup, -1, node_type=NT.INIT)
        self.connectBuffer = []
        self.taskgroup = taskgroup

    async def start(self):
        print("Starting server...")
        self.server = await asyncio.start_server(
            self.accept_connection, '127.0.0.1', 8888)
        async with self.server:
            await self.server.serve_forever()

    def accept_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        sock = writer.get_extra_info('socket')
        #Need to know what node to connect to
        #connect() just suppposed to advertise intent to connect
        #a new node is inserted when the loop node connects to the server of the new node,
        # then the oNode assignment for the new node and the iNode assignment for the next
        # node in the loop are directed by the insertion node
        if sock:
            sock_info = sock.getpeername()
            self.add_buffer_node(sock_info[0], sock_info[1], reader, writer)
            print(sock_info[0], ":", sock_info[1], "connected!")
            #print(sock.getsockopt('peername'))
        #self.connections.append(NodeLink())

    def add_buffer_node(self, ip, port, reader, writer):
        self.connectBuffer.append(Node(self.taskgroup, node_type=NT.INIT)
                                  .update_links_init(ip, port)
                                  .links[0][0].stream.open(reader, writer))

    async def init_loopback(self):
        print("Initializing loopback node...")
        await self.nodes[0].init_connect()
