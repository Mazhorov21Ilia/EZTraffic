import os
import yaml


def load_config(config_path=r"/home/sarah/Desktop/diploma/server/config/config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    required_fields = ["client_polling_interval_seconds", "clients"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    return config
