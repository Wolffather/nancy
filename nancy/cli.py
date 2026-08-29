from pathlib import Path
import click
from rich.console import Console

from nancy import ts_client
from nancy.config import load_config
from nancy.llm_client import LLMClient
from nancy.ts_client import TSClient
from nancy.generator import TestGenerator

console = Console()

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
@click.option('--output', '-o', help='Путь для сохранения сгенерированного файла (если не указан, выводится в консоль)')
@click.option('--interactive', '-i', is_flag=True, help='Интерактивный режим (редактирование, перегенерация)')
def generate(ticket_id, description, skill, language, framework, output, interactive):
    config = load_config()

    # Определяем контекст
    if ticket_id:
        ts = TSClient(config)
        try:
            issue = ts.get_issue(ticket_id)
            context = f"Заголовок: {issue['fields']['summary']}\nОписание: {issue['fields']['description']}"
        except Exception as e:
            console.print(f"[red]Ошибка чтения тикета: {e}[/]")
            return
    elif description:
        context = description
    else:
        console.print("[red]❌ Укажи либо ticket_id, либо --description[/]")
        return

    llm = LLMClient(config)
    generator = TestGenerator(llm, ts_client, skills_dir=config.get('SKILLS_DIR', 'skills'))

    with console.status("[bold green]Генерация теста...", spinner="dots"):
        test_code = generator.generate_test(
            context=context,
            skill_type=skill,
            language=language,
            framework=framework
        )

    # Если указан output — сохраняем в файл
    if output:
        output_path = Path(output)
        # Создаём родительские папки, если их нет
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Записываем код в файл (UTF-8)
        output_path.write_text(test_code, encoding='utf-8')
        console.print(f"[bold green]✅ Тест сохранён в {output_path}[/]")
    else:
        # Иначе выводим в консоль
        console.print("[bold green]✅ Тест сгенерирован![/]")
        console.print(test_code)

    if interactive:
        console.print("[yellow]Интерактивный режим пока в разработке[/]")

@cli.command(help="Показать доступные скиллы (файлы .md в папке skills/)")
def list_skills():
    skills_dir = Path("skills")
    if not skills_dir.exists():
        console.print("[red]Папка skills/ не найдена.[/]")
        return
    files = list(skills_dir.glob("*.md"))
    if not files:
        console.print("[yellow]Нет файлов .md в skills/[/]")
        return
    console.print("[bold]Доступные скиллы:[/]")
    for f in files:
        console.print(f"  - {f.stem}")

if __name__ == "__main__":
    cli()