import psutil
import time
import threading
import config.load_config as config

def collect_network():
    try:
        prev = psutil.net_io_counters()
        
        while True:
            time.sleep(1)
            curr = psutil.net_io_counters()
            
            in_delta = curr.bytes_recv - prev.bytes_recv
            out_delta = curr.bytes_sent - prev.bytes_sent
            
            with config.data_lock:
                config.traffic_data["in_bytes"] += max(0, in_delta)
                config.traffic_data["out_bytes"] += max(0, out_delta)
            
            prev = curr
            
    except Exception as e:
        time.sleep(5)
        print(f"Ошибка сбора трафика: {e}")
