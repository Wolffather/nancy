from pathlib import Path
from typing import Optional
from .default_prompts import (
    STRATEGY_PROJECT_TEMPLATE,
    PROJECT_TEMPLATE,
    TICKET_TEMPLATE,
    USER_TEMPLATE
)

class PromptBuilder:
    def __init__(self, template_dir):
        self.template_dir = Path(template_dir)
        self.cache = {}

    def _load_template(self, template_name: str) -> str:
        if template_name in self.cache:
            return self.cache[template_name]

        file_path = self.template_dir / template_name
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            self.cache[template_name] = content
            return content

        # fallback
        fallback = self._default_template(template_name)
        self.cache[template_name] = fallback
        return fallback

    def _default_template(self, template_name: str) -> str:
        """Возвращает встроенный шаблон, если файл не найден."""
        if "project" in template_name and "strategy" in template_name:
            return STRATEGY_PROJECT_TEMPLATE
        elif "project" in template_name:
            return PROJECT_TEMPLATE
        elif "ticket" in template_name:
            return TICKET_TEMPLATE
        else:
            return USER_TEMPLATE

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