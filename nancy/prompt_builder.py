from pathlib import Path


def _default_user_template():
    return """
Сгенерируй автотест на языке {language}
{fwk}
Описание сценария:
{context}
{feedback}
"""


class PromptBuilder:
    def __init__(self, template_dir="resources"):
        self.template_dir = Path(template_dir)
        self.user_template = self._load_template("user_prompt_template.md")

    def _load_template(self, filename):
        file_path = self.template_dir / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        else:
            # Встроенный fallback
            return _default_user_template()

    def build_user_prompt(self, context, language, framework=None, feedback=None):
        fwk = f"с использованием фреймворка {framework}" if framework else ""
        fb = f"\nУчти следующие замечания и исправь тест: {feedback}" if feedback else ""
        return self.user_template.format(
            language=language,
            fwk=fwk,
            context=context,
            feedback=fb
        )