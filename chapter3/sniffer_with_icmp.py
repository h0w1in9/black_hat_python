import socket
import os
import struct
from ctypes import *

# host to listen on
host = "192.168.199.141"


class ICMP(Structure):
    _fields_ = [("type", c_ubyte),
                ("code", c_ubyte),
                ("checksum", c_ushort),
                ("unused", c_ushort),
                ("next_hop_mtu", c_ushort)]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        pass


# our IP header
class IP(Structure):
    _fields_ = [("head_length", c_ubyte, 4),
                ("version", c_ubyte, 4),
                ("service_type", c_ubyte),
                ("length", c_ushort),
                ("identification", c_ushort),
                ("offset", c_ushort),
                ("ttl", c_ubyte),
                ("protocol_num", c_ubyte),
                ("checksum", c_ushort),
                ("src", c_uint32),
                ("dst", c_uint32)]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # map protocol constants to their names
        self.protocol_map = {1: "ICMP", 6: "TCP", 17: "UDP"}

        # human readable protocol
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

        # human readable IP addresses
        self.src_ip = socket.inet_ntoa(struct.pack("@I", self.src))
        self.dst_ip = socket.inet_ntoa(struct.pack("@I", self.dst))


if os.name == "nt":
    protocol_type = socket.IPPROTO_IP
else:
    protocol_type = socket.IPPROTO_ICMP
    # protocol_type = socket.IPPROTO_IP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol_type)

sniffer.bind((host, 0))

# we want the IP headers included in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# if we're using Windows, we need to send an IOCTL
# to set up promiscuous mode
if os.name == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while True:
        # read in a packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[:20])

        # print out the protocol that was detected and the hosts
        print "Protocol: %s  %s -> %s" % (ip_header.protocol, ip_header.src_ip, ip_header.dst_ip)

        # if it's ICMP, we want it
        if ip_header.protocol == "ICMP":
            offset=ip_header.head_length * 4
            icmp_header = ICMP(raw_buffer[offset:offset+sizeof(ICMP)])
            print "ICMP -> Type: %d Code: %d" %(icmp_header.type, icmp_header.code)


# handle CTRL-C
except KeyboardInterrupt:
    # if we're using Windows, turn off promiscuous mode
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
