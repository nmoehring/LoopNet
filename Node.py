import asyncio

from Message import Message
from NodeLink import NodeLink
from vocab import NodeType, LinkType, LinkDir, LT, LD


class Node:
    def __init__(self, taskgroup, node_id=1, node_type=NodeType.NET):
        self.taskgroup = taskgroup
        self.nodeId = node_id
        self.nodeType = node_type
        self.links = []
        for type_idx in range(len(LinkType)):
            self.links.append(NodeLink.as_pair(self, type_idx))
        self.inbox = asyncio.Queue()
        self.outbox = asyncio.Queue()
        self.taskgroup.create_task(self.run_mail_service())

    @classmethod
    def as_loopback(cls, taskgroup):
        new_node = cls(taskgroup, 0, node_type=NodeType.LOOPBACK)
        return new_node

    #   #######Node Type Checks#########
    def is_loopback(self):
        return self.nodeType is NodeType.LOOPBACK

    def is_alone(self):
        return self.links[LT.LOCAL][LD.IN].nodeId == self.nodeId

    #   #######Connection methods###############
    async def init_connect(self, ip, port):  # Connect to signal intent to be inserted in a net loop
        if self.nodeType == NodeType.INIT:
            self.links[LT.TEMP][LD.OUT].update(ip, port)
            await self.links[LT.TEMP][LD.OUT].open()
            await self.send_msg(["NEW_CONNECT", self.nodeId], 0)
        else:
            raise TypeError("init_connect() only meant to be called from INIT nodes.")

    #   # As node of a loop, connect to new node (connected with init_connect()) to insert them
    async def insert_connect(self, ip, port, node_id):
        self.update_link(ip, port, node_id, LT.TEMP, LD.OUT)
        await self.links[LT.TEMP][LD.OUT].open()

    #   ########Internal Link Manipulation##############
    def update_links_init(self, ip, port):
        if self.nodeType == NodeType.INIT:
            self.links[LT.TEMP][LD.IN].update(ip, port)
            return self
        else:
            raise AttributeError("This function to be used in INIT nodes.")

    def update_link(self, ip, port, node_id, link_type, link_dir):
        self.links[link_type][link_dir].update(ip, port, node_id)

    # ########MESSAGING########### #
    async def check_mail(self):
        while True:
            self.handle_msg(await self.inbox.get())

    async def send_mail(self):
        while True:
            (await self.outbox.get()).send()

    async def run_mail_service(self):
        self.taskgroup.create_task(self.check_mail())
        self.taskgroup.create_task(self.send_mail())

    def handle_msg(self, msg):
        data = msg.something()
        match data[0]:
            case 'NEW_CONNECT':
                self.insert_connect(data[1])

    async def insert_node(self, node_id, ip, port):
        temp = 0
        if not self.is_alone():
            await self.insert_connect(node_id, ip, port)  # Connect to new node
            insert_msg = ["INSERT_NODE", node_id, ip, port]
            await self.send_msg(insert_msg, LT.LOCAL)  # Send alert to current OUT
            # Receive INSERT_NODE message after complete loop, confirming good connection
            out_msg = ["NEW_OUTBOUND"] + self.links[LT.LOCAL][LD.OUT].get_info()
            await self.send_msg(out_msg, LT.TEMP)  # Msg new node with their new outbound
            # Message new node with their new outbound
            # (self if self was alone, else self's outbound)
        self.update_links(outbound_client_id=new_client_id,
                          outbound_ip=new_ip,
                          outbound_port=new_port)

    async def send_msg(self, message, link_idx):
        await self.outbox.put(Message.from_node(message, self, link_idx))

    async def print_msgs(self):
        print("MSG:", await self.links[0][0].stream.buffer.get)

    async def destroy(self):
        for link_pair in self.links:
            await link_pair[0].close()
            await link_pair[1].close()
        for link in self.tempLinks:
            await link.close()
