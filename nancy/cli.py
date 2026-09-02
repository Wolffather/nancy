from pathlib import Path
import click

from nancy.config import load_config, set_config_value, ALLOWED_SETTINGS_KEYS, SYNONYM_TO_KEY, CONFIG_PARAMETERS
from nancy.llm_client import LLMClient
from nancy.orchestrator import Orchestrator, determine_language
from nancy.ui import (
    show_error, show_success,
    show_available_skills, show_info, show_config_set_help,
    show_code, run_interactive_loop, show_spinner, show_current_config, prompt_save_to_file
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
    show_current_config()


@config.command(name="set", epilog="Для просмотра подробной справки выполните команду без аргументов.")
@click.argument('key', required=False)
@click.argument('value', required=False)
def config_set(key, value):
    """Установить значение параметра конфигурации."""
    if key is None or value is None:
        show_config_set_help()
        return

    env_key = SYNONYM_TO_KEY.get(key.lower())
    if env_key is None:
        env_key = key.upper()
        if env_key not in ALLOWED_SETTINGS_KEYS:
            show_error(f"Неизвестный параметр: {key}. Доступные: {', '.join(CONFIG_PARAMETERS.keys())}")
            return

    if env_key not in ALLOWED_SETTINGS_KEYS:
        show_error(f"Изменение параметра '{key}' запрещено.")
        return

    set_config_value(env_key, value)
    show_success(f"Параметр '{key}' установлен в '{value}'")


@cli.command()
@click.argument('ticket_id', required=False)
@click.option('--description', '-d', help='Текстовое описание сценария')
@click.option('--skill', '-s', default=None, help='Тип скилла')
@click.option('--framework', '-fw', default=None, help='Фреймворк для тестирования')
@click.option('--mock', is_flag=True, help='Использовать мок-клиент для трекер-системы')
@click.option('--output', '-o', help='Путь для сохранения результата')
@click.option('--project-path', '-p', help='Путь к проекту для автоматического анализа')
@click.option('--strategy', '-S', is_flag=True, help='Выдать предложение по стратегии тестирования вместо генерации кода')
def generate(ticket_id, description, skill, framework, mock, output, project_path, strategy):
    """Сгенерировать автотесты по входным параметрам."""
    config = load_config()

    # Подстановка дефолтов (язык больше не передаём)
    if skill is None:
        skill = config.get('DEFAULT_SKILL')
    # framework может быть None — оркестратор сам определит язык

    llm = LLMClient(config)
    orchestrator = Orchestrator(config, llm, mock=mock)

    # 1. Определяем язык до запуска спиннера
    language = determine_language(framework)

    # Запуск оркестратора (язык не передаём, он будет определён внутри)
    with show_spinner("Генерация..."):
        result = orchestrator.run(
            ticket_id=ticket_id,
            description=description,
            project_path=project_path,
            framework=framework,
            skill=skill,
            strategy=strategy,
            language=language
        )

    # Если указан output — просто сохраняем (с подтверждением)
    if output:
        show_code(result, language=language or 'java')
        action = prompt_save_to_file()
        if action.lower() == 'y':
            save_to_file(result, output)
            show_success(f"Тест сохранён в {output}")
        else:
            show_info("Файл не сохранён.")
        return

    # Если output не указан — запускаем интерактивный цикл (он покажет код и даст править)
    final_code = run_interactive_loop(
        initial_code=result,
        generator=orchestrator.generator,
        context=description or ticket_id or project_path or "Неизвестный сценарий",
        skill=skill,
        language=language,
        framework=framework
    )
    if final_code is not None and output:
        save_to_file(final_code, output)
        show_success(f"Финальный тест сохранён в {output}")


@cli.command(help="Показать доступные скиллы")
def list_skills():
    skills_dir = Path("skills")
    show_available_skills(skills_dir)


if __name__ == "__main__":
    cli()