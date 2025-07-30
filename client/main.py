import threading
from collector import *
import struct
import socket


SERVER_IP = '127.0.0.1'
SERVER_PORT = 5056


def open_conn():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', 5052))
    
    while True:
        data, addr = sock.recvfrom(1)
        if addr[0] == SERVER_IP:
            with data_lock:
                if traffic_data["in_bytes"] or traffic_data["out_bytes"]:
                    payload = struct.pack("!QQ", 
                                          traffic_data["in_bytes"], 
                                          traffic_data["out_bytes"])
                    sock.sendto(payload, (SERVER_IP, SERVER_PORT))
                    print(payload)
                    traffic_data["in_bytes"] = 0
                    traffic_data["out_bytes"] = 0
                    global last_activity
                    last_activity = time.time()


if __name__ == '__main__':
    threading.Thread(target=collect_network, daemon=True).start()
    threading.Thread(target=memory_clean, daemon=True).start()
    open_conn()