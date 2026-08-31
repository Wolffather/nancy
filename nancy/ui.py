from contextlib import contextmanager
from pathlib import Path
import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel

from nancy.config import CONFIG_PARAMETERS, load_config, get_default_framework_for_language

console = Console()


@contextmanager
def show_spinner(message: str):
    """Показывает анимированный спиннер во время выполнения блока."""
    with console.status(f"[bold green]{message}", spinner="dots"):
        yield


def show_settings(settings_dict: dict):
    """Показывает настройки в виде таблицы."""
    table = Table(title="Текущие настройки Nancy", style="bold cyan")
    table.add_column("Параметр", style="green")
    table.add_column("Значение", style="white")
    for key, value in settings_dict.items():
        table.add_row(key, str(value) if value is not None else "—")
    console.print(table)


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


def show_config_set_help():
    """Показывает справку по команде config set в виде таблицы."""
    table = Table(title="Доступные параметры для 'nancy config set'", style="bold cyan")
    table.add_column("Параметр", style="green", no_wrap=True)
    table.add_column("Синонимы", style="yellow")
    table.add_column("Описание", style="white")
    table.add_column("Значение по умолчанию", style="magenta")

    for key, info in CONFIG_PARAMETERS.items():
        synonyms = ", ".join(info['synonyms'])
        table.add_row(
            key,
            synonyms,
            info['description'],
            info['default']
        )

    console.print(table)
    console.print("\n[bold]Примеры:[/]")
    console.print("  [green]nancy config set language python[/]")
    console.print("  [green]nancy config set framework pytest+requests[/]")
    console.print("  [green]nancy config set llm_model qwen-plus[/]")
    console.print("  [green]nancy config set llm_temperature 0.7[/]")


def show_current_config():
    """Показывает текущие настройки в виде таблицы."""
    cfg = load_config()
    current_lang = cfg.get('DEFAULT_LANGUAGE')
    default_fw = get_default_framework_for_language(current_lang)
    current_fw = cfg.get('DEFAULT_FRAMEWORK')

    table = Table(title="Текущие настройки Nancy", style="bold cyan")
    table.add_column("Параметр", style="green")
    table.add_column("Значение", style="white")

    settings = [
        ("Язык по умолчанию", current_lang),
        ("Скилл по умолчанию", cfg.get('DEFAULT_SKILL')),
        ("Фреймворк по умолчанию", current_fw),
        ("Рекомендуемый фреймворк для языка", default_fw),
        ("Папка скиллов", cfg.get('SKILLS_DIR')),
        ("Папка шаблонов", cfg.get('TEMPLATE_DIR')),
        ("Модель LLM", cfg.get('LLM_MODEL', 'deepseek-chat')),
        ("Base URL", cfg.get('LLM_BASE_URL', 'https://api.deepseek.com/v1')),
        ("Температура", cfg.get('LLM_TEMPERATURE', 0.3)),
    ]

    for name, value in settings:
        table.add_row(name, str(value) if value is not None else "—")

    if current_fw and current_fw != default_fw:
        table.add_row("⚠️ Примечание", f"Фреймворк изменён вручную (не соответствует языку {current_lang})")

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
            return final_code

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