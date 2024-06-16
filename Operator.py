import asyncio
from Node import LoopNode
from Switchboard import Switchboard


class Operator:
    def __init__(self, client_id):
        self.id = client_id
        self.nodes = [LoopNode.as_loopback(client_id)]
        self.switchboard = Switchboard()
        self.newInboundConnections = asyncio.Queue()
        self.expectedInboundConnections = asyncio.Queue()

    def connect_to_loop(self, client_id, ip, port, category):
        #if newConnection.inputNode = loopNode #later, to prevent a single node from creating it's own hidden loop
        if len(self.nodes) == 1:
            self.nodes.append(client.connectNewClient(LoopNode(self.id)))

    async def start_switchboard(self):
        await self.switchboard.start()

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

    ####Broadcast functions
    def encryptMsg(self, message):
        pass

    def sendMsg(self, message, nodeIdx):
        self.nodes[nodeIdx].sendMsg(message)

    def sendDbgMsg(self, message):
        pass
    ####AsyncIO command center
