from contextlib import contextmanager
from pathlib import Path
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel

console = Console()

@contextmanager
def show_spinner(message: str):
    """Показывает анимированный спиннер во время выполнения блока."""
    with console.status(f"[bold green]{message}", spinner="dots"):
        yield


def show_success(message: str) -> None:
    console.print(f"[bold green]✅ {message}[/]")


def show_error(message: str) -> None:
    console.print(f"[bold red]❌ {message}[/]")


def show_info(message: str) -> None:
    console.print(f"[bold cyan]ℹ️ {message}[/]")


def show_warning(message: str) -> None:
    console.print(f"[bold yellow]⚠️ {message}[/]")


def show_code(code: str, language: str = "java") -> None:
    """Показывает код с подсветкой синтаксиса."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Сгенерированный код", border_style="cyan"))


def prompt_action() -> str:
    """Спрашивает пользователя, что делать с кодом."""
    console.print("\n[bold yellow]Что делаем?[/] (y — сохранить/выйти, n — перегенерировать, e — редактировать, c — отмена без сохранения)")
    return click.prompt("", type=click.Choice(['y', 'n', 'e', 'c'], case_sensitive=False), default='y')


def prompt_feedback() -> str:
    """Запрашивает замечания для перегенерации."""
    console.print("[bold yellow]Напиши, что исправить в тесте:[/]")
    return click.prompt("")


def show_available_skills(skills_dir: Path) -> None:
    """Показывает список доступных скиллов в виде таблицы."""
    if not skills_dir.exists():
        show_error(f"Папка skills/ не найдена: {skills_dir}")
        return

    files = list(skills_dir.glob("*.md"))
    if not files:
        show_warning("Нет файлов .md в папке skills/")
        return

    table = Table(title="Доступные скиллы", style="bold cyan")
    table.add_column("Имя", style="green")
    table.add_column("Описание", style="white")
    for f in files:
        # Пробуем прочитать первую строку как описание (если есть)
        description = ""
        try:
            content = f.read_text(encoding='utf-8')
            lines = content.split('\n')
            if lines and lines[0].startswith('#'):
                description = lines[0].lstrip('#').strip()
            else:
                description = "Без описания"
        except Exception:
            description = "Ошибка чтения"
        table.add_row(f.stem, description[:60] + ("..." if len(description) > 60 else ""))

    console.print(table)


def run_interactive_loop(
        initial_code: str,
        generator,
        context: str,
        skill: str,
        language: str,
        framework: str,
        output: str = None
) -> str:
    """
    Запускает интерактивный цикл: показывает код, принимает команды,
    перегенерирует или открывает редактор. Возвращает финальный код или None при отмене.
    """
    final_code = initial_code
    while True:
        show_code(final_code, language)
        action = prompt_action()

        if action == 'y':
            return final_code  # сохраним снаружи

        elif action == 'n':
            feedback = prompt_feedback()
            with console.status("[bold green]Перегенерирую с учётом замечаний...", spinner="dots"):
                final_code = generator.generate_test(
                    context=context,
                    skill_type=skill,
                    language=language,
                    framework=framework,
                    feedback=feedback
                )
            show_success("Новая версия готова.")

        elif action == 'e':
            from .utils import open_in_editor
            try:
                final_code = open_in_editor(final_code, language)
                show_success("Код обновлён из редактора.")
            except Exception as e:
                show_error(str(e))

        elif action == 'c':
            show_warning("Отмена. Тест не сохранён.")
            return None