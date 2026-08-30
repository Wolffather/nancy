from pathlib import Path
from .prompt_builder import PromptBuilder

class TestGenerator:
    def __init__(self, llm_client, skills_dir="skills", template_dir="resources"):
        self.llm = llm_client
        self.skills_dir = Path(skills_dir)
        self.prompt_builder = PromptBuilder(template_dir)

    def generate_test(self, context, skill_type, language, framework=None, feedback=None):
        # Загружаем системный промпт (скилл)
        system_prompt = self._load_skill(skill_type)

        # Строим пользовательский промпт
        user_prompt = self.prompt_builder.build_user_prompt(
            context=context,
            language=language,
            framework=framework,
            feedback=feedback
        )

        # Вызываем LLM
        return self.llm.generate(user_prompt, system_prompt)

    def _load_skill(self, skill_type):
        skill_file = self.skills_dir / f"{skill_type}.md"
        if skill_file.exists():
            return skill_file.read_text(encoding="utf-8")
        default_file = self.skills_dir / "default.md"
        if default_file.exists():
            return default_file.read_text(encoding="utf-8")
        return "Ты — эксперт по автоматизации тестирования. Генерируй качественный код."