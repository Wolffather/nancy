from pathlib import Path
from typing import Optional
from .base import Analyzer
from .java import JavaAnalyzer
from .python import PythonAnalyzer
from .javascript import JavaScriptAnalyzer


def get_analyzer(language: str, project_path: Path) -> Analyzer:
    """Возвращает анализатор для указанного языка."""
    lang_map = {
        "java": JavaAnalyzer,
        "python": PythonAnalyzer,
        "javascript": JavaScriptAnalyzer,
        "js": JavaScriptAnalyzer,
        "typescript": JavaScriptAnalyzer,  # пока заглушка
    }
    analyzer_class = lang_map.get(language.lower())
    if not analyzer_class:
        raise ValueError(f"Неподдерживаемый язык: {language}")
    return analyzer_class(project_path)


def detect_language(project_path: Path) -> str:
    """
    Автоматически определяет язык проекта по наличию файлов.
    Сначала проверяет стандартные файлы сборки, затем ищет файлы по расширениям.
    """
    # 1. Проверка по файлам сборки
    if (project_path / "pom.xml").exists():
        return "java"
    if (project_path / "build.gradle").exists() or (project_path / "gradle.build").exists():
        return "java"   # тоже java
    if (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
        return "python"
    if (project_path / "package.json").exists():
        return "javascript"

    # 2. Если нет файлов сборки, ищем по расширениям в подпапках (рекурсивно)
    # Ограничим поиск, чтобы не сканировать большие папки — проверяем до 5 файлов
    java_files = list(project_path.rglob("*.java"))
    if java_files:
        return "java"
    py_files = list(project_path.rglob("*.py"))
    if py_files:
        return "python"
    js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
    if js_files:
        return "javascript"

    # 3. Если ничего не нашли — ошибка
    raise ValueError(
        "Не удалось определить язык проекта. Укажите --language явно (java, python, javascript)."
    )