import unittest

from Operator import Operator
from NodeLink import NodeLink


class MyTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = Operator(1)

    async def testConnection(self):
        await self.client.start_server()
        await self.client.nodes[0].init_connect()
        await self.client.nodes[0].send("TEST123")


if __name__ == '__main__':
    unittest.main()
