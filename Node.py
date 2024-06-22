import asyncio

from Message import Message
from NodeLink import NodeLink
from enum import Enum


def to_code(num, num_bits=8, int_size=256):
    # Original number, number of bits for original encoding, evenly divided across 64 bits
    num_shifts = int(int_size / num_bits)
    new_num = int(num)
    for shift in range(num_shifts):
        new_num = new_num << num_bits
        new_num = new_num | num
    return new_num


class Category(Enum):  # 256 categories. Uses repetition error-correcting code, 8 repetitions across 64 bits
    Loopback = 0
    MainNet = to_code(1)
    LAN = to_code(2)  # these 4 are more about speed than distance, but I like the names
    WAN = to_code(3)
    VWAN = to_code(4)
    AsLongAsItTakesNet = to_code(5)
    InitLink = to_code(6)


class Node:
    def __init__(self, taskgroup, node_id=1, category=Category.MainNet):
        self.taskgroup = taskgroup
        self.node_id = node_id
        self.category = category
        self.links = []
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

    async def insert_node(self, new_client_id, new_ip, new_port):
        # Message outbound node that they will get a new connection for their inbound
        await self.send_msg(f'INSERTNODE\n{new_client_id}\n{new_ip}\n{new_port}\n')
        if not self.is_alone():
            pass
#           #Receive message confirming successful
#           #Message new node with their new inbound (self) and their new outbound
#           # (self if self was alone, else self's outbound)
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
