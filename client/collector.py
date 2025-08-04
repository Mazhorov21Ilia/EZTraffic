import psutil
import time
import threading

data_lock = threading.Lock()
last_activity = time.time()


def memory_clean(traffic_data, last_activity, lock):
    try:
        with lock:
            # Обнуляем счётчики
            traffic_data["in_bytes"] = 0
            traffic_data["out_bytes"] = 0
            # Обновляем метку времени
            last_activity[0] = time.time()
    except Exception as e:
        print(f"Ошибка при очистке памяти: {e}")
        raise


