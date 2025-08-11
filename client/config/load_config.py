import yaml
from pathlib import Path
import time
import threading

traffic_data = {
    "in_bytes": 0,
    "out_bytes": 0
}

data_lock = threading.RLock()

last_activity = time.time()

def return_yaml():
    try:
        with open(f"{Path(__file__).parent}\\config.yaml", "r") as file:
            return yaml.safe_load(file)

    except FileNotFoundError:
        print("Файл не найден")
        raise
    except yaml.YAMLError as e:
        print(f"Ошибка парсинга YAML файла: {e}")
        raise

yaml_data = return_yaml()