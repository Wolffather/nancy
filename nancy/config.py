# nancy/config.py
import os
from dotenv import load_dotenv


def load_config():
    # Ищем .env в текущей директории
    load_dotenv()  # по умолчанию ищет .env

    return {
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'SKILLS_DIR': os.getenv('SKILLS_DIR', 'skills'),
        'TS_URL': os.getenv('TS_URL'),  # вместо JIRA_URL
        'TS_EMAIL': os.getenv('TS_EMAIL'),
        'TS_API_TOKEN': os.getenv('TS_API_TOKEN'),
    }