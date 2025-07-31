import socket
import threading
import time
import struct
from config.load_config import return_yaml


try:
    yaml_data = return_yaml()
except Exception as e:
    print(f"Ошибка при импорте конфигурации: {e}")
    raise


SERVER_IP = yaml_data['SERVER_IP']  # Слушать все интерфейсы
SERVER_PORT = yaml_data['SERVER_PORT']
AGENT_ADDRESSES = [(yaml_data['AGENT_IP'], yaml_data['AGENT_PORT'])]  # Список агентов (IP, PORT)
POLL_INTERVAL = yaml_data['POLL_INTERVAL']  # Интервал опроса агентов (сек)

def start_polling():
    """Поток опроса агентов"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    while True:
        for agent_addr in AGENT_ADDRESSES:
            sock.sendto(b"\x01", agent_addr)  # 1 байт вместо строки
        time.sleep(POLL_INTERVAL)

def handle_incoming_data():
    """Обработка входящих данных от агентов"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    
    print(f"[SERVER] Запущен на {SERVER_IP}:{SERVER_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(16)  # 16 байт = 2x uint64
            if len(data) == 16:
                in_bytes, out_bytes = struct.unpack("!QQ", data)
                print(f"Получено от {addr[0]}: вход={in_bytes} байт, выход={out_bytes} байт")
                # Здесь можно сохранять данные в БД или файл
            else:
                print(f"[WARN] Некорректные данные от {addr}")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    # Запускаем опрос в фоне
    threading.Thread(target=start_polling, daemon=True).start()
    # Основной поток обработки данных
    handle_incoming_data()