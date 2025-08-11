import socket
import threading
import struct
import time
import config.load_config as config
from collector import collect_network
from cleaner import memory_clean

AGENT_IP = config.yaml_data['AGENT_IP']
AGENT_PORT = config.yaml_data['AGENT_PORT']
SERVER_IP = config.yaml_data['SERVER_IP']
SERVER_PORT = config.yaml_data['SERVER_PORT']
MEMORY_CLEAR_TIMEOUT = config.yaml_data['MEMORY_CLEAR_TIMEOUT']



def memory_cleanup():
    while True:
        time.sleep(1)
        if time.time() - config.last_activity > MEMORY_CLEAR_TIMEOUT:
            memory_clean()
            print(f"Автоочистка: прошло {MEMORY_CLEAR_TIMEOUT} сек без активности")

def handle_server_requests():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((AGENT_IP, AGENT_PORT))
    print(f"Агент запущен на {AGENT_IP}:{AGENT_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1)
            
            if addr[0] == SERVER_IP and data == b"\x01":
                with config.data_lock:
                    if config.traffic_data["in_bytes"] or config.traffic_data["out_bytes"]:
                        payload = struct.pack(
                            "!QQ", 
                            config.traffic_data["in_bytes"], 
                            config.traffic_data["out_bytes"]
                        )
                        sock.sendto(payload, (SERVER_IP, SERVER_PORT))
                        print(f"Отправлено: in={config.traffic_data['in_bytes']}, out={config.traffic_data['out_bytes']}")
                memory_clean()
        except Exception as e:
            print(f"Ошибка обработки: {e}")


if __name__ == "__main__":
    threading.Thread(target=collect_network, daemon=True).start()
    threading.Thread(target=memory_cleanup, daemon=True).start()
    handle_server_requests()