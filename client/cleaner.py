import time
import config.load_config as config

def memory_clean():
    with config.data_lock:
        config.traffic_data["in_bytes"] = 0
        config.traffic_data["out_bytes"] = 0
        
        config.last_activity = time.time()
    
    print("[CLEANER] Данные очищены, last_activity обновлен")