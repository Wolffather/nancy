import os
from pathlib import Path
import click

from nancy.config import load_config, set_config_value, ALLOWED_SETTINGS_KEYS, get_default_framework_for_language, \
    SYNONYM_TO_KEY, CONFIG_PARAMETERS
from nancy.llm_client import LLMClient
from nancy.orchestrator import Orchestrator
from nancy.request_builder import RequestBuilder
from nancy.ui import (
    console,
    show_error, show_success,
    show_available_skills,
    show_settings, show_info, show_config_set_help, run_interactive_loop, show_code, show_spinner
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


def show_current_config():
    pass


@config.command(name="show")
def config_show():
    """Показать текущие настройки (безопасные параметры)"""
    show_current_config()


@config.command(name="set", epilog="Для просмотра подробной справки выполните команду без аргументов.")
@click.argument('key', required=False)
@click.argument('value', required=False)
def config_set(key, value, env_key=None):
    """Установить значение параметра конфигурации."""
    # Если ключ или значение не переданы — показываем справку
    if key is None or value is None:
        show_config_set_help()
        return

    # Проверяем допустимость
    if env_key not in ALLOWED_SETTINGS_KEYS:
        show_error(f"Изменение параметра '{key}' запрещено.")
        return

    # Сохраняем старые значения (если есть)
    old_lang = os.getenv('NANCY_DEFAULT_LANGUAGE')
    old_framework = os.getenv('NANCY_DEFAULT_FRAMEWORK')

    # Устанавливаем новое значение
    set_config_value(env_key, value)
    show_success(f"Параметр '{key}' установлен в '{value}'")

    # Если меняем язык, автоматически подбираем фреймворк
    if env_key == 'NANCY_DEFAULT_LANGUAGE':
        new_lang = value
        default_fw = get_default_framework_for_language(new_lang)
        if old_lang:
            old_default_fw = get_default_framework_for_language(old_lang)
            # Если текущий фреймворк равен старому дефолтному или не задан, то обновляем
            current_fw = os.getenv('NANCY_DEFAULT_FRAMEWORK')
            if current_fw == old_default_fw or current_fw is None:
                set_config_value('NANCY_DEFAULT_FRAMEWORK', default_fw)
                show_info(f"Фреймворк автоматически изменён на '{default_fw}' для языка {new_lang}")
        else:
            # Если старого языка не было, просто устанавливаем дефолтный фреймворк
            set_config_value('NANCY_DEFAULT_FRAMEWORK', default_fw)
            show_info(f"Фреймворк автоматически установлен на '{default_fw}' для языка {new_lang}")


@cli.command()
@click.argument('ticket_id', required=False)
@click.option('--description', '-d', help='Текстовое описание сценария')
@click.option('--skill', '-s', default='api', help='Тип скилла')
@click.option('--language', '-lp', help='Язык программирования (переопределяет дефолт)')
@click.option('--framework', '-fw', help='Фреймворк (переопределяет дефолт)')
@click.option('--mock', is_flag=True, help='Использовать мок-клиент для трекер-системы')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим')
@click.option('--output', '-o', help='Путь для сохранения результата')
def generate(ticket_id, description, skill, language, framework, mock, interactive, output):
    config = load_config()
    llm = LLMClient(config)
    orchestrator = Orchestrator(config, llm, mock=mock)

    # Формируем запрос через билдер
    user_request = RequestBuilder.build(
        ticket_id=ticket_id,
        description=description,
        language=language,
        framework=framework,
        skill=skill
    )

    # Генерация
    with show_spinner("Генерация теста..."):
        result = orchestrator.run(user_request, skill=skill)

    # Если не интерактив и не output — просто выводим
    if not interactive:
        if output:
            save_to_file(result, output)
            show_success(f"Тест сохранён в {output}")
        else:
            console.print(result)
        return

    # Интерактивный режим
    # Для интерактива нам нужен генератор, который умеет перегенерировать
    # Пока используем существующую логику (может быть доработана)
    final_code = result
    if interactive:
        # Используем run_interactive_loop из ui
        final_code = run_interactive_loop(
            initial_code=result,
            generator=orchestrator.generator,  # передаём генератор
            context=description or ticket_id,
            skill=skill,
            language=language or config.get('DEFAULT_LANGUAGE'),
            framework=framework or config.get('DEFAULT_FRAMEWORK'),
            output=output
        )
        if final_code is None:
            return
        if output:
            save_to_file(final_code, output)
            show_success(f"Финальный тест сохранён в {output}")
        else:
            show_code(final_code, language or config.get('DEFAULT_LANGUAGE'))


@cli.command(help="Показать доступные скиллы")
def list_skills():
    skills_dir = Path("skills")
    show_available_skills(skills_dir)


if __name__ == "__main__":
    cli()