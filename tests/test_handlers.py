from socket_listener.handlers import PacketHandler
from socket_listener.packet import Packet


def test_empty_packet():
    ph = PacketHandler()
    p1 = Packet(b"")
    ph.handle_packet(p1)
