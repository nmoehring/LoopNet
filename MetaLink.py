from lingo import LD


class MetaLink:
    def __init__(self, host_node_id, host_link_type, addr, port, reader=None, writer=None):
        self.hostNodeId = int(host_node_id)
        self.hostLinkType = host_link_type
        self.addr = str(addr)
        self.port = int(port)
        self.reader = reader
        self.writer = writer
        self.hostLink = None
        self.parentNode = None

    @classmethod
    def from_list(cls, list_sock):
        return cls(list_sock[0], list_sock[1], list_sock[2])

    @classmethod
    def from_streams(cls, reader, writer):
        sock = writer.get_extra_info('socket')
        if sock:
            sock_info = sock.getpeername()
            return cls(1, sock_info[0], sock_info[1], reader, writer)

    def __eq__(self, other):
        if (type(other) is type(self) and self.hostNodeId == other.hostNodeId and
                self.addr == other.addr and self.port == other.port):
            return True
        else:
            return False

    def update_node(self, in_mlink):
        if self.parentNode:
            self.parentNode.update_link(self.ip, self.port, 1, self.hostLinkType, LD.IN)
            self.parentNode.links[self.hostLinkType][LD.IN].stream.open(self.reader, self.writer)
        else:
            raise AttributeError("No parent node set for the metalink that called updateNode.")