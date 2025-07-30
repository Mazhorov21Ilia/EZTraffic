import socket
import threading
import time
import struct
from collector import *

# Конфигурация
AGENT_IP = "0.0.0.0"
AGENT_PORT = 5005
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5006
MEMORY_CLEAR_TIMEOUT = 60  # Таймаут очистки памяти (сек)

data_lock = threading.Lock()


def handle_server_requests():
    """Обработка запросов от сервера"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((AGENT_IP, AGENT_PORT))
    print(f"[AGENT] Запущен на {AGENT_IP}:{AGENT_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1)
            # Проверяем: запрос от сервера + корректная команда
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