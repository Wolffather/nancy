from pathlib import Path
import click

from nancy.config import load_config, set_config_value, ALLOWED_SETTINGS_KEYS
from nancy.llm_client import LLMClient
from nancy.ts_client import TSClient   # теперь он сам умеет мокать
from nancy.generator import TestGenerator
from nancy.ui import (
    show_error, show_success, show_code,
    run_interactive_loop, show_available_skills, show_spinner,
    show_settings
)
from nancy.utils import save_to_file


@click.group()
def cli():
    """Nancy — AI-агент для автоматизации тестирования"""
    pass


@cli.group()
def config():
    """Управление настройками Nancy"""
    pass


@config.command(name="show")
def config_show():
    """Показать текущие настройки (безопасные параметры)"""
    cfg = load_config()
    display = {
        "Язык по умолчанию": cfg.get('DEFAULT_LANGUAGE'),
        "Скилл по умолчанию": cfg.get('DEFAULT_SKILL'),
        "Фреймворк по умолчанию": cfg.get('DEFAULT_FRAMEWORK'),
        "Папка скиллов": cfg.get('SKILLS_DIR'),
        "Папка шаблонов": cfg.get('TEMPLATE_DIR'),
    }
    show_settings(display)


@config.command(name="set")
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Установить значение параметра (только безопасные: language, skill, framework, skills_dir, template_dir)"""
    mapping = {
        'language': 'NANCY_DEFAULT_LANGUAGE',
        'lang': 'NANCY_DEFAULT_LANGUAGE',
        'skill': 'NANCY_DEFAULT_SKILL',
        'framework': 'NANCY_DEFAULT_FRAMEWORK',
        'fw': 'NANCY_DEFAULT_FRAMEWORK',
        'skills_dir': 'SKILLS_DIR',
        'template_dir': 'TEMPLATE_DIR',
    }
    env_key = mapping.get(key.lower())
    if env_key is None:
        env_key = key.upper()
        if env_key not in ALLOWED_SETTINGS_KEYS:
            show_error(f"Неизвестный параметр: {key}. Допустимые: language, skill, framework, skills_dir, template_dir")
            return

    if env_key not in ALLOWED_SETTINGS_KEYS:
        show_error(f"Изменение параметра '{key}' запрещено (можно менять только: language, skill, framework, skills_dir, template_dir)")
        return

    set_config_value(env_key, value)
    show_success(f"Параметр '{key}' установлен в '{value}'")


@cli.command(help="Сгенерировать тест по тикету (Jira) или текстовому описанию")
@click.argument('ticket_id', required=False, metavar='[TICKET_ID]')
@click.option('--description', '-d', help='Текстовое описание сценария (если нет тикета)')
@click.option('--skill', '-s', help='Тип скилла: api, load, ui, default, security, bdd')
@click.option('--language', '-lp', type=click.Choice(['java', 'python', 'javascript', 'csharp', 'go', 'ruby'], case_sensitive=False), help='Язык программирования')
@click.option('--framework', '-fw', help='Фреймворк для тестирования')
@click.option('--output', '-o', help='Путь для сохранения сгенерированного файла')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим')
@click.option('--mock', is_flag=True, help='Использовать мок-клиент для трекер-системы (без реального API)')
def generate(ticket_id, description, skill, language, framework, output, interactive, mock):
    config = load_config()

    # Подстановка дефолтов из конфига
    if language is None:
        language = config.get('DEFAULT_LANGUAGE')
    if skill is None:
        skill = config.get('DEFAULT_SKILL')
    if framework is None:
        framework = config.get('DEFAULT_FRAMEWORK')

    # Определяем контекст
    if ticket_id:
        # Передаём флаг mock в TSClient
        ts = TSClient(config, mock=mock)
        try:
            issue = ts.get_issue(ticket_id)
            context = f"Заголовок: {issue['fields']['summary']}\nОписание: {issue['fields']['description']}"
        except Exception as e:
            show_error(f"Ошибка чтения тикета: {e}")
            return
    elif description:
        context = description
    else:
        show_error("Укажи либо ticket_id, либо --description")
        return

    # Инициализация
    llm = LLMClient(config)
    generator = TestGenerator(
        llm,
        skills_dir=config.get('SKILLS_DIR', 'skills'),
        template_dir=config.get('TEMPLATE_DIR', 'resources')
    )

    # Генерация со спиннером
    with show_spinner("Генерация теста..."):
        test_code = generator.generate_test(
            context=context,
            skill_type=skill,
            language=language,
            framework=framework
        )

    # Если не интерактив — сохраняем или выводим
    if not interactive:
        if output:
            save_to_file(test_code, output)
            show_success(f"Тест сохранён в {output}")
        else:
            show_code(test_code, language)
        return

    # Интерактивный режим
    final_code = run_interactive_loop(
        initial_code=test_code,
        generator=generator,
        context=context,
        skill=skill,
        language=language,
        framework=framework,
        output=output
    )

    if final_code is None:
        return

    # Сохраняем финальную версию
    if output:
        save_to_file(final_code, output)
        show_success(f"Тест сохранён в {output}")
    else:
        show_code(final_code, language)


@cli.command(help="Показать доступные скиллы")
def list_skills():
    skills_dir = Path("skills")
    show_available_skills(skills_dir)


if __name__ == "__main__":
    cli()