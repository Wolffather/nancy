import os
from pathlib import Path
import click

from nancy.config import load_config, set_config_value, ALLOWED_SETTINGS_KEYS, \
    SYNONYM_TO_KEY, CONFIG_PARAMETERS
from nancy.llm_client import LLMClient
from nancy.orchestrator import Orchestrator
from nancy.ui import (
    console,
    show_error, show_success,
    show_available_skills,
    show_info, show_config_set_help,
    show_code, run_interactive_loop, show_spinner, show_current_config
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

    # Определяем полное имя переменной
    env_key = SYNONYM_TO_KEY.get(key.lower())
    if env_key is None:
        env_key = key.upper()
        if env_key not in ALLOWED_SETTINGS_KEYS:
            show_error(f"Неизвестный параметр: {key}. Доступные: {', '.join(CONFIG_PARAMETERS.keys())}")
            return

    if env_key not in ALLOWED_SETTINGS_KEYS:
        show_error(f"Изменение параметра '{key}' запрещено.")
        return

    # Устанавливаем значение (без дополнительной логики)
    set_config_value(env_key, value)
    show_success(f"Параметр '{key}' установлен в '{value}'")


@cli.command()
@click.argument('ticket_id', required=False)
@click.option('--description', '-d', help='Текстовое описание сценария')
@click.option('--skill', '-s', default=None, help='Тип скилла')
@click.option('--language', '-lp', default=None, help='Язык программирования')
@click.option('--framework', '-fw', default=None, help='Фреймворк')
@click.option('--mock', is_flag=True, help='Использовать мок-клиент для трекер-системы')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим')
@click.option('--output', '-o', help='Путь для сохранения результата')
@click.option('--project-path', '-p', help='Путь к проекту для автоматического анализа')
@click.option('--strategy', '-S', is_flag=True, help='Выдать предложение по стратегии тестирования вместо генерации кода')
def generate(ticket_id, description, skill, language, framework, mock, interactive, output, project_path, strategy):
    config = load_config()
    # Подстановка дефолтов
    if skill is None:
        skill = config.get('DEFAULT_SKILL')
    if language is None:
        language = config.get('DEFAULT_LANGUAGE')
    if framework is None:
        framework = config.get('DEFAULT_FRAMEWORK')

    config = load_config()
    llm = LLMClient(config)
    orchestrator = Orchestrator(config, llm, mock=mock)

    # Запуск оркестратора с переданными параметрами
    with show_spinner("Генерация теста..."):
        result = orchestrator.run(
            ticket_id=ticket_id,
            description=description,
            project_path=project_path,
            language=language,
            framework=framework,
            skill=skill,
            strategy=strategy   # передаём флаг
        )

    # Если не интерактив — просто выводим или сохраняем
    if not interactive:
        if output:
            save_to_file(result, output)
            show_success(f"Тест сохранён в {output}")
        else:
            console.print(result)
        return

    # Интерактивный режим (только если не стратегия, иначе смысла нет)
    if strategy:
        show_info("Режим стратегии не поддерживает интерактивный режим.")
        return

    final_code = run_interactive_loop(
        initial_code=result,
        generator=orchestrator.generator,
        context=description or ticket_id or project_path or "Неизвестный сценарий",
        skill=skill,
        language=language or config.get('DEFAULT_LANGUAGE'),
        framework=framework or config.get('DEFAULT_FRAMEWORK'),
        output=output
    )
    if output:
        save_to_file(final_code, output)
        show_success(f"Финальный тест сохранён в {output}")
    else:
        show_code(final_code, language or config.get('DEFAULT_LANGUAGE'))

@cli.command(help="Запустить веб-интерфейс Nancy")
@click.option('--host', default='0.0.0.0', help='Хост для сервера')
@click.option('--port', default=8000, type=int, help='Порт для сервера')
@click.option('--reload', is_flag=True, help='Включить авто-перезагрузку при изменениях (для разработки)')
def web(host, port, reload):
    """Запускает веб-интерфейс Nancy."""
    from nancy.web.app import run_server
    click.echo(f"🌐 Запуск веб-интерфейса на http://{host}:{port}")
    run_server(host=host, port=port, reload=reload)


@cli.command(help="Показать доступные скиллы")
def list_skills():
    skills_dir = Path("skills")
    show_available_skills(skills_dir)


if __name__ == "__main__":
    cli()