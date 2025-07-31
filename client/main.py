import socket
import threading
import time
import struct
from collector import *
from config.load_config import return_yaml


try:
    yaml_data = return_yaml()
except Exception as e:
    print(f"Ошибка при импорте конфигурации: {e}")
    raise

AGENT_IP = yaml_data['AGENT_IP']
AGENT_PORT = yaml_data['AGENT_PORT']
SERVER_IP = yaml_data['SERVER_IP']
SERVER_PORT = yaml_data['SERVER_PORT']
MEMORY_CLEAR_TIMEOUT = yaml_data['MEMORY_CLEAR_TIMEOUT']

data_lock = threading.Lock()


def handle_server_requests():
    """Обработка запросов от сервера"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((AGENT_IP, AGENT_PORT))
    print(f"[AGENT] Запущен на {AGENT_IP}:{AGENT_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1)
            if addr[0] == SERVER_IP and data == b"\x01":
                with data_lock:
                    # Формируем пакет только если есть данные
                    if traffic_data["in_bytes"] or traffic_data["out_bytes"]:
                        payload = struct.pack(
                            "!QQ", 
                            traffic_data["in_bytes"], 
                            traffic_data["out_bytes"]
                        )
                        sock.sendto(payload, (SERVER_IP, SERVER_PORT))
                        traffic_data["in_bytes"] = 0
                        traffic_data["out_bytes"] = 0
                        global last_activity
                        last_activity = time.time()
                        print("[AGENT] Данные отправлены серверу")
        except Exception as e:
            print(f"[AGENT ERROR] {e}")

if __name__ == "__main__":
    threading.Thread(target=collect_network, daemon=True).start()
    threading.Thread(target=memory_clean, daemon=True).start()
    handle_server_requests()