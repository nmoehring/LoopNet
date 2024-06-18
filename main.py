import asyncio
from Operator import Operator

TESTING = False


async def main():
    op = Operator(1)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(op.start_all_systems(tg))


if __name__ == '__main__':
    asyncio.run(main())

    if TESTING:
        def init_test_net(num_test_clients):
            return [Operator(idx) for idx in range(num_test_clients)]


        numClients = 10
        testClients = init_test_net(numClients)

        for client in testClients[1:numClients]:
            client.connect_to_loop(testClients[0])

        for client in testClients:
            print("Client:", client.id, "In:", client.nodes[1].connection.inboundNode.routingId, "Out:",
                  client.nodes[1].connection.outboundNode.routingId, "Cat:", client.nodes[1].connection.category)

#------------Testing-----------------------
