from server.main import *
from config.config_m import load_config

config = load_config()
start_polling(config)