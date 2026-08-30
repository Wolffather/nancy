import os
from dotenv import load_dotenv, set_key

CONFIG_FILE = ".env"

ALLOWED_SETTINGS_KEYS = [
    "NANCY_DEFAULT_LANGUAGE",
    "NANCY_DEFAULT_SKILL",
    "NANCY_DEFAULT_FRAMEWORK",
    "SKILLS_DIR",
    "TEMPLATE_DIR",
]

SHOW_SETTINGS_KEYS = [
    "NANCY_DEFAULT_LANGUAGE",
    "NANCY_DEFAULT_SKILL",
    "NANCY_DEFAULT_FRAMEWORK",
    "SKILLS_DIR",
    "TEMPLATE_DIR",
]

def load_config():
    load_dotenv()
    return {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'TS_URL': os.getenv('TS_URL'),
        'TS_EMAIL': os.getenv('TS_EMAIL'),
        'TS_API_TOKEN': os.getenv('TS_API_TOKEN'),
        'MOCK_TS': os.getenv('MOCK_TS', 'false').lower() == 'true',  # преобразуем в bool
        'SKILLS_DIR': os.getenv('SKILLS_DIR', 'skills'),
        'TEMPLATE_DIR': os.getenv('TEMPLATE_DIR', 'resources'),
        'DEFAULT_LANGUAGE': os.getenv('NANCY_DEFAULT_LANGUAGE', 'java'),
        'DEFAULT_SKILL': os.getenv('NANCY_DEFAULT_SKILL', 'api'),
        'DEFAULT_FRAMEWORK': os.getenv('NANCY_DEFAULT_FRAMEWORK', 'junit5+restassured'),
    }

def get_config_value(key):
    return os.getenv(key)

def set_config_value(key, value):
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            f.write("")
    set_key(CONFIG_FILE, key, value)