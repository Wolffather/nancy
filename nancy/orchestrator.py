from pathlib import Path
from nancy import ui
from nancy.generator import TestGenerator
from nancy.prompt_builder import PromptBuilder
from nancy.ts_client import TSClient
from nancy.utils import get_frameworks_to_languages_mapping


def _format_project_structure(structure: dict, max_classes: int = 50, max_methods_per_class: int = 10) -> str:
    """
    Форматирует структуру проекта, ограничивая количество классов и методов.
    """
    lines = []
    classes = structure.get("classes", [])
    total_classes = len(classes)

    if total_classes > max_classes:
        lines.append(f"⚠️ Проект содержит {total_classes} классов. Показаны первые {max_classes}.")
        classes = classes[:max_classes]

    for cls in classes:
        package = cls.get('package', 'default')
        lines.append(f"Класс {cls['name']} (пакет {package})")
        methods = cls.get("methods", [])
        if len(methods) > max_methods_per_class:
            lines.append(f"  (всего {len(methods)} методов, показаны первые {max_methods_per_class})")
            methods = methods[:max_methods_per_class]

        for method in methods:
            params = method.get('params', [])
            param_names = []
            for p in params:
                if isinstance(p, dict):
                    param_names.append(p.get('name', ''))
                else:
                    param_names.append(str(p))
            params_str = ", ".join(param_names)
            return_type = method.get('return_type', 'void')
            lines.append(f"  - метод {method['name']}({params_str}) -> {return_type}")

    if not lines:
        return "Не найдено классов или методов для анализа."

    return "\n".join(lines)


def determine_language(framework: str) -> str:
    """Определяет язык по фреймворку, или возвращает None, если нужно спросить."""
    if not framework:
        return None  # будет использован дефолтный язык из конфига

    # Маппинг фреймворк → язык
    mapping = get_frameworks_to_languages_mapping()

    fw_lower = framework.lower()
    for key, lang in mapping.items():
        if key in fw_lower:
            if lang is None:
                # Мультиязычный фреймворк — спрашиваем
                return ui.prompt_language()
            return lang

    # Если не нашли — возвращаем None (будет использован дефолт)
    return None


class Orchestrator:
    def __init__(self, config, llm_client, mock=False):
        self.config = config
        self.llm = llm_client
        self.mock = mock
        self.ts_client = TSClient(config, mock=mock)
        self.prompt_builder = PromptBuilder(
            template_dir=config['PROMPTS_DIR']
        )
        self.generator = TestGenerator(
            llm_client,
            skills_dir=config['SKILLS_DIR'],
            prompt_builder=self.prompt_builder
        )

    def run(self, *,
            ticket_id=None,
            description=None,
            project_path=None,
            framework=None,
            skill="api",
            strategy=False,
            language=None):
        """
        Основной метод оркестрации.
        Определяет язык на основе фреймворка, если это возможно, иначе запрашивает у пользователя.
        """

        # Определяем контекст и шаблон
        if project_path:
            from nancy.analyzers.factory import get_analyzer, detect_language
            try:
                lang = language or detect_language(Path(project_path))
            except ValueError as e:
                ui.show_error(f"[red]{e}[/]")
                return
            analyzer = get_analyzer(lang, Path(project_path))
            project_structure = analyzer.analyze()
            context_str = _format_project_structure(project_structure)
            if strategy:
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
        ui.show_debug_message("Загружен шаблон " + template_name)
        user_prompt = self.prompt_builder.build_prompt(
            context=context_str,
            language=language or self.config.get('DEFAULT_LANGUAGE', 'java'),
            framework=framework,
            template_name=template_name,
            skill=skill
        )

        # Отправляем в LLM
        return self.llm.generate(user_prompt, system_prompt)

    def _load_skill(self, skill_name: str) -> str:
        """
        Загружает скилл, автоматически включая best_practices.md (если он существует).
        Если skill_name == "best_practices", загружается только он (без дублирования).
        """
        skills_dir = Path(self.config.get('SKILLS_DIR', 'skills'))
        best_practices_file = skills_dir / "best_practices.md"
        skill_file = skills_dir / f"{skill_name}.md"

        # Если запрошен специально best_practices, загружаем только его
        if skill_name == "best_practices":
            if best_practices_file.exists():
                return best_practices_file.read_text(encoding='utf-8')
            return ""

        parts = []

        # 1. Добавляем best_practices, если есть
        if best_practices_file.exists():
            parts.append(best_practices_file.read_text(encoding='utf-8'))

        # 2. Добавляем основной скилл (или default, если его нет)
        if skill_file.exists():
            parts.append(skill_file.read_text(encoding='utf-8'))
        else:
            default_file = skills_dir / "default.md"
            if default_file.exists():
                parts.append(default_file.read_text(encoding='utf-8'))

        # Если ничего не загружено — возвращаем базовый промпт
        if not parts:
            return "Ты — эксперт по автоматизации тестирования. Генерируй качественный код."

        # Объединяем части с разделителем
        return "\n\n---\n\n".join(parts)