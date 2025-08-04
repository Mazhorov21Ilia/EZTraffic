import socket
import threading
import time
import struct
from collector import *
from config.load_config import return_yaml

last_activity = [time.time()]
traffic_data = {"in_bytes": 0, "out_bytes": 0}
data_lock = threading.Lock()

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


def collect_network():
    try:
        prev = psutil.net_io_counters()
        global traffic_data
        while True:
            time.sleep(1)
            curr = psutil.net_io_counters()
            with data_lock:
                traffic_data["in_bytes"] += curr.bytes_recv - prev.bytes_recv
                traffic_data["out_bytes"] += curr.bytes_sent - prev.bytes_sent  
                prev = curr
                # print(traffic_data)
            

    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")
        raise

def memory_cleanup():
    """Фоновый таймер очистки памяти"""
    
    while True:
        current_time = time.time()
        
        with data_lock:
            elapsed = current_time - last_activity[0]
        
        if elapsed > MEMORY_CLEAR_TIMEOUT:
            memory_clean(traffic_data, last_activity, data_lock)
            print(f"[AGENT] Автоочистка: данные сброшены (таймаут {MEMORY_CLEAR_TIMEOUT} сек)")
        time.sleep(1)

def handle_server_requests():
    """Обработка запросов от сервера"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((AGENT_IP, AGENT_PORT))
    print(f"[AGENT] Запущен на {AGENT_IP}:{AGENT_PORT}")

    while True:
        # try:
            data, addr = sock.recvfrom(1)
            if True: # addr[0] == SERVER_IP and data == b"\x01":
                payload = None
                with data_lock:
                    payload = struct.pack(
                        "!QQ", 
                        traffic_data["in_bytes"], 
                        traffic_data["out_bytes"]
                    )
                    memory_clean(traffic_data, last_activity, data_lock)
                sock.sendto(payload, (SERVER_IP, SERVER_PORT))
                print("[AGENT] Данные отправлены серверу")

        # except Exception as e:
        #     print(f"Ошибка при обработке запроса от сервера: {e}")

if __name__ == "__main__":
    threading.Thread(target=collect_network, daemon=True).start()
    threading.Thread(target=memory_cleanup, daemon=True).start()
    handle_server_requests()