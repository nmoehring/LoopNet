import unittest

from Operator import Operator
from Connection import LoopConnection


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = Operator(1)

    async def testConnection(self):
        await self.client.start_server()
        await self.client.nodes[0].connect()
        await self.client.nodes[0].send("TEST123")


if __name__ == '__main__':
    unittest.main()
