import socket, struct, random, time

TARGET_PORT = 12333

if __name__ == "__main__":
    packer = struct.Struct('f')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.sendto(packer.pack(random.random()), ('127.0.0.1', TARGET_PORT))

    # will scroll from one side to the other
    for i in range(100):
        sock.sendto(packer.pack(i/100.0), ('127.0.0.1', TARGET_PORT))
        time.sleep(0.01)
