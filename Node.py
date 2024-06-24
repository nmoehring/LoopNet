import asyncio

from Mail import Mail
from NodeLink import NodeLink
from lingo import NodeType, LinkType, LT, LD, NS, NodeState, LM


class Node:
    def __init__(self, taskgroup, invites, inbox, outbox, node_id=1, node_type=NodeType.NET):
        self.taskgroup = taskgroup
        self.nodeId = node_id
        self.nodeType = node_type
        self.links = []
        self.invites = invites
        self.inbox = inbox
        self.outbox = outbox
        for type_idx in range(len(LinkType)):
            self.links.append(NodeLink.as_pair(self, type_idx))
        self.status = NodeState.STEADY
        self.metaLinkBuffer = []

    @classmethod
    def as_loopback(cls, taskgroup, invites, inbox, outbox):
        new_node = cls(taskgroup, invites, inbox, outbox, 0, node_type=NodeType.LOOPBACK)
        return new_node

    #   #######Node Type Checks#########
    def is_loopback(self):
        return self.nodeType is NodeType.LOOPBACK

    def is_alone(self):
        return self.links[LT.LOCAL][LD.IN].nodeId == self.nodeId

    #   #######Connection methods###############
    async def init_connect(self):  # Connect to signal intent to be inserted in a net loop
        # if self.nodeType == NodeType.INIT:
        await self.links[LT.TEMP][LD.OUT].open()
        await self.send_msg(["INSERT_NEW_CONNECT", self.nodeId], 0)
        self.status = NodeState.INSERT_NEW_CONNECT
        # else:
            # raise TypeError("init_connect() only meant to be called from INIT nodes.")

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

    async def begin_insert(self, node_id, ip, port):
        if not self.is_alone():
            await self.insert_connect(node_id, ip, port)  # Connect to new node
            insert_msg = [LM.INSERT_EXPECT, node_id, ip, port]
            await self.send_msg(insert_msg, LT.LOCAL)  # Send alert to current OUT
            # Receive INSERT_NODE message after complete loop, confirming good connection
            out_msg = [LM.INSERT_CONNECT_OB] + self.links[LT.LOCAL][LD.OUT].get_info()
            await self.send_msg(out_msg, LT.TEMP)  # Msg new node with their new outbound
            self.status = NodeState.WAIT_INSERTION
        else:
            out_msg = [LM.INSERT_CONNECT_OB] + self.links[LT.LOCAL][LD.OUT].get_info()
            await self.send_msg(out_msg, LT.TEMP)
            self.status = NodeState.WAIT_2LOOP

    async def finish_insert(self):
        if self.status == NodeState.WAIT_INSERTION:
            await self.send_msg(LM.INSERT_LOOP_CLOSED, LT.LOCAL)
            await self.send_msg(LM.INSERT_LOOP_CLOSED, LT.TEMP)
            self.reset_temp_links()
        elif self.status == NodeState.WAIT_2LOOP:
            await self.send_msg(LM.INSERT_LOOP_CLOSED, LT.LOCAL)
            self.reset_temp_links()

    async def send_msg(self, message, link_idx):
        await self.outbox.put(Mail.from_node(message, self, link_idx))

    async def destroy(self):
        for link_pair in self.links:
            await link_pair[LD.IN].close()
            await link_pair[LD.OUT].close()

    def reset_temp_links(self):
        self.links[LT.TEMP][LD.IN].close()
        self.links[LT.TEMP][LD.OUT].close()
