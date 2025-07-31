import yaml
from pathlib import Path

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
