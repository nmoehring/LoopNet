import asyncio
from Node import Node
from Switchboard import Switchboard


class Operator:
    def __init__(self):
        self.callsign = None
        self.switchboard = Switchboard()

    async def start_all_systems(self, taskgroup):
        taskgroup.create_task(self.switchboard.start())
        #taskgroup.create_task(self.switchboard.init_loopback())

    async def run_nodes(self, taskGroup):
        pass

    def insertNewClient(self, connectingNode):
        selectedNode = self.selectNodeForInsertion(connectingNode)
        selectedNode.insert_node(connectingNode)
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
