import asyncio
from Node import Node
from Switchboard import Switchboard


class Operator:
    def __init__(self, taskgroup):
        self.taskgroup = taskgroup
        self.callsign = None
        self.switchboard = Switchboard(taskgroup)

    async def start_all_systems(self):
        self.taskgroup.create_task(self.switchboard.start())
        self.taskgroup.create_task(self.switchboard.init_loopback())
        self.taskgroup.create_task(self.switchboard.process_queues())

    async def run_nodes(self):
        pass

    def insertNewClient(self, connectingNode):
        selectedNode = self.selectNodeForInsertion(connectingNode)
        selectedNode.begin_insert(connectingNode)
        return connectingNode

    def selectNodeForInsertion(self, connectingNode):
        if len(self.nodes) == 1:
            self.nodes.append(Node(self.id))
        return self.nodes[1]

    def encryptMsg(self, message):
        pass

    def sendMsg(self, message, nodeIdx):
        self.nodes[nodeIdx].sendMsg(message)

    def sendDbgMsg(self, message):
        pass
