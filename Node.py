import asyncio
from Connection import LoopConnection
from enum import Enum


def to_code(num, num_bits=8, int_size=256):
    #Original number, number of bits for original encoding, evenly divided across 64 bits
    num_shifts = int(int_size / num_bits)
    new_num = int(num)
    for shift in range(num_shifts):
        new_num = new_num << num_bits
        new_num = new_num | num
    return new_num


class Category(Enum):  #256 categories. Uses repetition error-correcting code, 8 repetitions across 64 bits
    Loopback = 0
    MainNet = to_code(1)
    LAN = to_code(2)  #these 4 are more about speed than distance, but I like the names
    WAN = to_code(3)
    VWAN = to_code(4)
    AsLongAsItTakesNet = to_code(5)


class LoopNode:
    def __init__(self, client_id, connection, category=Category.MainNet):
        self.clientId = client_id
        self.category = category
        self.outConnection = connection
        self.inQ = asyncio.Queue()
        self.outQ = asyncio.Queue()

    @classmethod
    def as_loopback(cls, client_id):
        return cls(client_id, LoopConnection.as_loopback(client_id), category=Category.Loopback)

    def is_loopback(self):
        return self.category is Category.Loopback

    def is_alone(self):
        return self.outConnection.clientId == self.clientId

    async def connect(self):
        await self.outConnection.accept_connection()

    def update_connections(self, outbound_client_id=None, outbound_ip=None, outbound_port=None, category=None):
        self.outConnection.update(outbound_client_id, outbound_ip, outbound_port)
        if category:
            self.category = category
        return self

    async def insert_node(self, new_client_id, new_ip, new_port):
        # Message outbound node that they will get a new connection for their inbound
        await self.send_msg(f'NEW NODE\n{new_client_id}\n{new_ip}\n{new_port}\n')
        if not self.is_alone():
            pass
            #Receive message confirming successful
            #Message new node with their new inbound (self) and their new outbound
            # (self if self was alone, else self's outbound)
        self.update_connections(outbound_client_id=new_client_id,
                                outbound_ip=new_ip,
                                outbound_port=new_port)

    async def send_msg(self, message):
        await self.outConnection.send(message)
