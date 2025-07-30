import psutil
import time
import threading

data_lock = threading.Lock()
last_activity = time.time()
traffic_data = {"in_bytes": 0, "out_bytes": 0}

def collect_network():
    try:
        prev = psutil.net_io_counters()
        while True:
            time.sleep(1)
            curr = psutil.net_io_counters()
            with data_lock:
                traffic_data["in_bytes"] += curr.bytes_recv - prev.bytes_recv
                traffic_data["out_bytes"] += curr.bytes_sent - prev.bytes_sent
            prev = curr
    except Exception as e:
        print(f"Ошибка при сборе данных: {e}")
        raise


def memory_clean():
    try:
        global last_activity
        while True:
            time.sleep(1)
            if time.time() - last_activity > 60:
                with data_lock:
                    print("[AGENT] Очистка памяти по таймауту")
                    traffic_data["in_bytes"] = 0
                    traffic_data["out_bytes"] = 0
                    last_activity = time.time()
    except Exception as e:
        print(f"Ошибка при очистке памяти: {e}")
        raise


