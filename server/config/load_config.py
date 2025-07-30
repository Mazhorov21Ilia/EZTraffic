import yaml


def return_yaml():
    try:
        with open("config.yaml", "r") as file:
            data = yaml.safe_load(file)


    except FileNotFoundError:
        print("Файл не найден")
        raise
    except yaml.YAMLError as e:
        print(f"Ошибка парсинга YAML файла: {e}")
        raise
