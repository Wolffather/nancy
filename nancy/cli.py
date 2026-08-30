from pathlib import Path
import click

from nancy.config import load_config
from nancy.llm_client import LLMClient
from nancy.ts_client import TSClient
from nancy.generator import TestGenerator
from nancy.ui import (
    show_error, show_success, show_code,
    run_interactive_loop, show_available_skills, show_spinner
)
from nancy.utils import save_to_file


@click.group()
def cli():
    """Nancy — AI-агент для автоматизации тестирования"""
    pass


@cli.command(help="Сгенерировать тест по тикету (Jira) или текстовому описанию")
@click.argument('ticket_id', required=False, metavar='[TICKET_ID]')
@click.option('--description', '-d', help='Текстовое описание сценария (если нет тикета)')
@click.option('--skill', '-s', default='api', show_default=True, help='Тип скилла: api, load, ui, default, security, bdd')
@click.option('--language', '-lp', default='java', show_default=True, type=click.Choice(['java', 'python', 'javascript', 'csharp', 'go', 'ruby'], case_sensitive=False), help='Язык программирования')
@click.option('--framework', '-fw', help='Фреймворк для тестирования (например: junit5+restassured, pytest+requests, jest+supertest)')
@click.option('--output', '-o', help='Путь для сохранения сгенерированного файла')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим')
def generate(ticket_id, description, skill, language, framework, output, interactive):
    config = load_config()

    # Определяем контекст
    if ticket_id:
        ts = TSClient(config)
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