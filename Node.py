import asyncio

from Message import Message
from NodeLink import NodeLink
from vocab import Category, LinkLevel


class Node:
    def __init__(self, taskgroup, node_id=1, category=Category.MainNet):
        self.taskgroup = taskgroup
        self.node_id = node_id
        self.category = category
        self.links = []
        for level in range(4):
            if category is Category.MainNet:
                self.links.append(NodeLink.as_netlink_pair(self, level))
        self.inbox = asyncio.Queue()
        self.outbox = asyncio.Queue()
        if category == Category.Loopback:
            self.links.append(NodeLink.as_netlink_pair(self, 0))
        else:
            self.links.append(NodeLink.as_netlink_pair(self, 0))
        self.tempLinks = []
        self.taskgroup.create_task(self.run_mail_service())
        self.inQ = asyncio.Queue()  # figure out how to block data in one direction on a socket
        self.outQ = asyncio.Queue()

    @classmethod
    def as_loopback(cls, taskgroup):
        new_node = cls(taskgroup, 0, category=Category.Loopback)
        new_node.loopback_id = -1
        return new_node

    #   #######Node Type Checks#########
    def is_loopback(self):
        return self.category is Category.Loopback

    def is_alone(self):
        return self.links[0][0].node_id == self.node_id

    #   #######Connection methods###############
    async def init_connect(self, ip, port):  # Connect to signal intent to be inserted in a net loop
        if self.category == Category.InitLink:
            self.links[0][1].update(ip, port)
            await self.links[0][1].open()
            await self.send_msg(["NEW_CONNECT", self.node_id], 0)
        else:
            raise TypeError("init_connect() only meant to be called from InitLink nodes.")

    #   # As node of a loop, connect to new node (connected with init_connect()) to insert them
    async def insert_connect(self, ip, port, node_id):
        pass

    #   ########Internal Link Manipulation##############
    def update_links_init(self, ip, port):
        if self.category == Category.InitLink:
            self.links[0][0].update(ip, port)
            return self
        else:
            raise AttributeError("This function to be used in InitLink nodes.")

    def update_links(self, outbound_client_id=None, outbound_ip=None, outbound_port=None, category=None):
        self.links[0][1].update(outbound_client_id, outbound_ip, outbound_port)
        if category:
            self.category = category
        return self

    #   #########MESSAGING###########
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

    async def insert_node(self, new_node_id, new_ip, new_port):
        temp = 0
        if not self.is_alone():
            self.tempLinks.append(NodeLink(self, new_ip, new_port, 0, 1, new_node_id, False))
            await self.tempLinks[0].open()
            await self.send_msg(["INSERT_NODE", new_node_id, new_ip, new_port], 0)
            # Receive INSERT_NODE message after complete loop, confirming good connection
            await self.send_msg(["NEW_OUTPUT", ])
            # Message new node with their new inbound (self) and their new outbound
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
