from pathlib import Path
from typing import Optional

class PromptBuilder:
    def __init__(self, template_dir="nancy/prompts"):
        self.template_dir = Path(template_dir)
        self.cache = {}

    def _load_template(self, template_name: str) -> str:
        if template_name in self.cache:
            return self.cache[template_name]

        file_path = self.template_dir / template_name
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            self.cache[template_name] = content
            print(f"[DEBUG] Загружен шаблон: {file_path}")
            return content

        print(f"[WARN] Шаблон {template_name} не найден, использую fallback")
        fallback = self._default_template(template_name)
        self.cache[template_name] = fallback
        return fallback

    def _default_template(self, template_name: str) -> str:
        """Возвращает встроенный шаблон, если файл не найден."""
        if "project" in template_name and "strategy" in template_name:
            return """
Ты — эксперт по тестированию. Проанализируй структуру проекта на языке {language} и предложи стратегию тестирования с учётом выбранного скилла: {skill}.

Учитывай:
- Какие классы и методы нуждаются в тестировании.
- Какие типы тестов (юнит, интеграционные, e2e, нагрузочные, UI, безопасность) наиболее подходят.
- Какие фреймворки и инструменты лучше использовать для этого типа тестирования.
- Какие сценарии должны быть покрыты в первую очередь.

Не генерируй код автотестов — только описание стратегии на русском языке.

Структура проекта:
{context}
{feedback}
"""
        elif "project" in template_name:
            return """
Проанализируй проект на языке {language} и сгенерируй тесты для всех публичных методов с учётом скилла {skill} {fwk}.

Структура проекта:
{context}
{feedback}
"""
        elif "ticket" in template_name:
            return """
Тикет:
{context}

Сгенерируй автотест на языке {language} с учётом скилла {skill}
{fwk}
{feedback}
"""
        else:
            return """
Сгенерируй автотест на языке {language} с учётом скилла {skill}
{fwk}
Описание сценария:
{context}
{feedback}
"""

    def build_prompt(
        self,
        context: str,
        language: str = "java",
        framework: Optional[str] = None,
        feedback: Optional[str] = None,
        template_name: str = "user_prompt_template.md",
        skill: Optional[str] = None,
    ) -> str:
        template = self._load_template(template_name)
        fwk = f"с использованием фреймворка {framework}" if framework else ""
        fb = f"\nУчти следующие замечания и исправь тест: {feedback}" if feedback else ""
        skill_value = skill or "api"
        return template.format(
            language=language,
            fwk=fwk,
            context=context,
            feedback=fb,
            skill=skill_value,
        )