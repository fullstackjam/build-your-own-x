import socket
import struct
import sys
import time

def main(dest_name):
    dest_addr = socket.gethostbyname(dest_name)
    print(f"Traceroute to {dest_name} ({dest_addr}), 30 hops max")

    icmp_protocol = socket.getprotobyname('icmp')
    udp_protocol = socket.getprotobyname('udp')

    for ttl in range(1, 31):
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp_protocol)
        recv_socket.settimeout(2)
        recv_socket.bind(("", 33434))

        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp_protocol)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        send_socket.sendto(b"", (dest_addr, 33434))

        curr_addr = None
        curr_name = None
        try:
            data, curr_addr = recv_socket.recvfrom(512)
            curr_addr = curr_addr[0]
            try:
                curr_name = socket.gethostbyaddr(curr_addr)[0]
            except socket.error:
                curr_name = curr_addr
        except socket.error:
            pass
        finally:
            send_socket.close()
            recv_socket.close()

        if curr_addr is not None:
            print(f"{ttl}. {curr_name} ({curr_addr})")
        else:
            print(f"{ttl}. *")

        if curr_addr == dest_addr:
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <destination>")
        sys.exit(1)

    main(sys.argv[1])
