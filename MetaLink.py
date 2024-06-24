from LinkStream import LinkStream
from lingo import LD


class MetaLink:
    def __init__(self, host_node_id, client_node_id, client_addr, client_port,
                 parent=None, host_link_type=None, reader=None, writer=None):
        self.hostNodeId = int(host_node_id)
        self.clientNodeId = client_node_id
        self.hostLinkType = host_link_type
        self.clientAddr = str(client_addr)
        self.clientPort = int(client_port)
        self.linkStream = LinkStream(self, reader, writer)
        self.parentNode = parent

    @classmethod
    def from_list(cls, list_sock):
        return cls(list_sock[0], list_sock[1], list_sock[2], list_sock[3])

    @classmethod
    def from_streams(cls, reader, writer, parent=None):
        sock = writer.get_extra_info('socket')
        if sock:
            sock_info = sock.getpeername()
            return cls(1, 1, sock_info[0], sock_info[1],
                       parent=parent, reader=reader, writer=writer)

    def __eq__(self, other):
        if (type(other) is type(self) and self.hostNodeId == other.hostNodeId and
                self.clientAddr == other.clientAddr and self.clientPort == other.clientPort):
            return True
        else:
            return False

    def prepare_node_update(self, in_mlink):
        self.parentNode.metaLinkBuffer.append(MetaLink(
            self.hostNodeId, in_mlink.clientNodeId, self.clientAddr,
            self.clientPort, self.hostLinkType, in_mlink.reader, in_mlink.writer))

    def update_node(self, in_mlink):
        if self.parentNode:
            self.parentNode.update_link(self.ip, self.clientPort, 1, self.hostLinkType, LD.IN)
            self.parentNode.links[self.hostLinkType][LD.IN].stream.open(self.reader, self.writer)
        else:
            raise AttributeError("No parent node set for the metalink that called updateNode.")