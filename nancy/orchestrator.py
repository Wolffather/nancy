from pathlib import Path

from nancy import ui
from nancy.generator import TestGenerator
from nancy.prompt_builder import PromptBuilder
from nancy.ts_client import TSClient


class Orchestrator:
    def __init__(self, config, llm_client, mock=False):
        self.config = config
        self.llm = llm_client
        self.mock = mock
        self.ts_client = TSClient(config, mock=mock)
        self.generator = TestGenerator(
            llm_client,
            skills_dir=config.get('SKILLS_DIR', 'skills')
        )
        self.prompt_builder = PromptBuilder()

    def run(self, *,
            ticket_id=None,
            description=None,
            project_path=None,
            language=None,
            framework=None,
            skill="api",
            strategy=False):
        """
        Основной метод оркестрации: определяет источник контекста,
        строит промпт и отправляет в LLM.
        """
        # Определяем контекст и выбираем шаблон
        if project_path:
            from nancy.analyzers.factory import get_analyzer, detect_language
            try:
                lang = language or detect_language(Path(project_path))
            except ValueError as e:
                # Предложить пользователю указать язык
                ui.show_error(f"[red]{e}[/]")
                return
            analyzer = get_analyzer(lang, Path(project_path))
            project_structure = analyzer.analyze()
            context_str = self._format_project_structure(project_structure)
            if strategy :
                template_name = "project_strategy_prompt_template.md"
            else:
                template_name = "project_prompt_template.md"
        elif ticket_id:
            issue = self.ts_client.get_issue(ticket_id)
            context_str = f"Заголовок: {issue['fields']['summary']}\nОписание: {issue['fields']['description']}"
            template_name = "ticket_prompt_template.md"
        else:
            context_str = description or "Не указан сценарий"
            template_name = "user_prompt_template.md"

        # Сборка системного промпта (скилл)
        system_prompt = self._load_skill(skill)
        # Сборка пользовательского промпта
        user_prompt = self.prompt_builder.build_prompt(
            context=context_str,
            language=language or self.config.get('DEFAULT_LANGUAGE', 'java'),
            framework=framework or self.config.get('DEFAULT_FRAMEWORK'),
            template_name=template_name
        )

        # Отправляем в LLM (без тулов, т.к. всё уже собрано)
        return self.llm.generate(user_prompt, system_prompt)

    def _format_project_structure(self, structure: dict) -> str:
        """Форматирует структуру проекта в читаемый текст для промпта."""
        lines = []
        for cls in structure.get("classes", []):
            package = cls.get('package', 'default')
            lines.append(f"Класс {cls['name']} (пакет {package})")
            for method in cls.get("methods", []):
                params = ", ".join([p.get('name', '') for p in method.get('params', [])])
                return_type = method.get('return_type', 'void')
                lines.append(f"  - метод {method['name']}({params}) -> {return_type}")
        if not lines:
            return "Не найдено классов или методов для анализа."
        return "\n".join(lines)

    def _load_skill(self, skill_name: str) -> str:
        """Загружает системный промпт (скилл) из папки skills/."""
        skills_dir = Path(self.config.get('SKILLS_DIR', 'skills'))
        skill_file = skills_dir / f"{skill_name}.md"
        if skill_file.exists():
            return skill_file.read_text(encoding='utf-8')
        default_file = skills_dir / "default.md"
        if default_file.exists():
            return default_file.read_text(encoding='utf-8')
        return "Ты — эксперт по автоматизации тестирования. Генерируй качественный код."