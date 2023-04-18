import socket
import time
import struct
import select
import sys
from functools import reduce

def checksum(data):
    data = bytearray(data)
    csum = 0
    count_to = (len(data) // 2) * 2

    for count in range(0, count_to, 2):
        this_val = data[count + 1] * 256 + data[count]
        csum = csum + this_val
        csum = csum & 0xffffffff

    if count_to < len(data):
        csum = csum + data[-1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

def create_packet(id):
    header = struct.pack('bbHHh', 8, 0, 0, id, 1)
    data = struct.pack('d', time.time())

    chksum = checksum(header + data)
    header = struct.pack('bbHHh', 8, 0, socket.htons(chksum), id, 1)

    return header + data

def ping(host):
    icmp_protocol = socket.getprotobyname('icmp')
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
    packet_id = int((id(0) % 65535))
    packet = create_packet(packet_id)

    sock.sendto(packet, (host, 0))
    start_time = time.time()

    while True:
        timeout = 1 - (time.time() - start_time)
        if timeout < 0:
            return None

        ready = select.select([sock], [], [], timeout)
        if ready[0] == []:
            return None

        recv_packet, addr = sock.recvfrom(1024)
        icmp_header = recv_packet[20:28]
        icmp_type, _, _, packet_id, _ = struct.unpack('bbHHh', icmp_header)

        if icmp_type == 0 and packet_id == packet_id:
            return time.time() - start_time

if __name__ == '__main__':
    target_host = sys.argv[1] if len(sys.argv) > 1 else 'www.example.com'
    print(f"Pinging {target_host}...")

    for i in range(5):
        delay = ping(target_host)
        if delay is None:
            print("Request timed out")
        else:
            delay *= 1000
            print(f"Reply from {target_host}: time={delay:.2f} ms")
        time.sleep(1)
