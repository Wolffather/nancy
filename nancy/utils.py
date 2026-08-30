import os
import subprocess
import tempfile
from pathlib import Path

def get_file_extension(language: str) -> str:
    """Возвращает расширение файла для заданного языка."""
    mapping = {
        "java": ".java",
        "python": ".py",
        "javascript": ".js",
        "csharp": ".cs",
        "go": ".go",
        "ruby": ".rb",
    }
    return mapping.get(language.lower(), ".txt")

def open_in_editor(content: str, language: str) -> str:
    """
    Открывает содержимое в системном редакторе и возвращает отредактированный текст.
    """
    suffix = get_file_extension(language)
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode='w', encoding='utf-8') as tf:
        tf.write(content)
        temp_path = tf.name

    editor = os.environ.get('EDITOR')
    if not editor:
        if os.name == 'nt':
            editor = 'notepad'
        else:
            editor = 'nano'

    try:
        subprocess.call([editor, temp_path])
    except FileNotFoundError:
        raise RuntimeError(f"Редактор '{editor}' не найден. Установи EDITOR (например, export EDITOR=code)")

    edited_content = Path(temp_path).read_text(encoding='utf-8')
    Path(temp_path).unlink(missing_ok=True)
    return edited_content

def save_to_file(content: str, output_path: str) -> None:
    """Сохраняет содержимое в файл, создавая родительские папки при необходимости."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')