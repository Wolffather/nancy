import os
from dotenv import load_dotenv, set_key

CONFIG_FILE = ".env"

# Описание всех конфигурируемых параметров
CONFIG_PARAMETERS = {
    'NANCY_DEFAULT_LANGUAGE': {
        'synonyms': ['language', 'lang'],
        'description': 'язык программирования (java, python, javascript, csharp, go, ruby)',
        'default': 'java',
    },
    'NANCY_DEFAULT_SKILL': {
        'synonyms': ['skill'],
        'description': 'тип скилла (api, load, ui, default, security, bdd)',
        'default': 'api',
    },
    'NANCY_DEFAULT_FRAMEWORK': {
        'synonyms': ['framework', 'fw'],
        'description': 'фреймворк для тестирования (например, junit5+restassured)',
        'default': 'junit5+restassured',
    },
    'SKILLS_DIR': {
        'synonyms': ['skills_dir'],
        'description': 'папка со скиллами',
        'default': 'skills',
    },
    'TEMPLATE_DIR': {
        'synonyms': ['template_dir'],
        'description': 'папка с шаблонами промптов',
        'default': 'resources',
    },
    'LLM_MODEL': {
        'synonyms': ['llm_model'],
        'description': 'модель LLM (например, deepseek-chat, qwen-plus)',
        'default': 'deepseek-chat',
    },
    'LLM_BASE_URL': {
        'synonyms': ['llm_base_url'],
        'description': 'базовый URL для API LLM',
        'default': 'https://api.deepseek.com/v1',
    },
    'LLM_TEMPERATURE': {
        'synonyms': ['llm_temperature'],
        'description': 'температура (0.0 - 1.0)',
        'default': '0.3',
    },
}

# Список разрешённых ключей для изменения (используется в cli.py)
ALLOWED_SETTINGS_KEYS = list(CONFIG_PARAMETERS.keys())

# Маппинг синонимов на полные имена
SYNONYM_TO_KEY = {}
for key, info in CONFIG_PARAMETERS.items():
    for syn in info['synonyms']:
        SYNONYM_TO_KEY[syn] = key

def load_config():
    load_dotenv()
    # Строим конфиг на основе CONFIG_PARAMETERS
    config = {}
    for key, info in CONFIG_PARAMETERS.items():
        env_value = os.getenv(key)
        if env_value is None:
            config[key] = info['default']
        else:
            # Для LLM_TEMPERATURE приводим к float
            if key == 'LLM_TEMPERATURE':
                config[key] = float(env_value)
            else:
                config[key] = env_value

    # Специальные ключи (не описанные в CONFIG_PARAMETERS)
    config['LLM_API_KEY'] = os.getenv('LLM_API_KEY')
    config['TS_URL'] = os.getenv('TS_URL')
    config['TS_EMAIL'] = os.getenv('TS_EMAIL')
    config['TS_API_TOKEN'] = os.getenv('TS_API_TOKEN')
    config['MOCK_TS'] = os.getenv('MOCK_TS', 'false').lower() == 'true'
    config['TS_API_PATH'] = os.getenv('TS_API_PATH')
    config['SKILLS_DIR'] = os.getenv('SKILLS_DIR')
    config['PROMPTS_DIR'] = os.getenv('PROMPTS_DIR')
    config['TEMPLATES_DIR'] = os.getenv('TEMPLATES_DIR')

    # Алиасы для удобства
    config['DEFAULT_LANGUAGE'] = config.get('NANCY_DEFAULT_LANGUAGE')
    config['DEFAULT_SKILL'] = config.get('NANCY_DEFAULT_SKILL')
    config['DEFAULT_FRAMEWORK'] = config.get('NANCY_DEFAULT_FRAMEWORK')
    config['SKILLS_DIR'] = config.get('SKILLS_DIR')
    config['PROMPTS_DIR'] = config.get('PROMPTS_DIR')
    config['TEMPLATES_DIR'] = config.get('TEMPLATES_DIR')

    return config

def get_config_value(key):
    return os.getenv(key)

def set_config_value(key, value):
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            f.write("")
    set_key(CONFIG_FILE, key, value)