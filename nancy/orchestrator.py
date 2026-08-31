import json
from pathlib import Path
from nancy.tools import get_tools_schema
from nancy.ts_client import TSClient
from nancy.generator import TestGenerator
from nancy.utils import save_to_file, open_in_editor
from nancy.ui import show_info


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

    def run(self, user_request: str, skill: str = "api"):
        tools_schema = get_tools_schema()

        # Первый вызов LLM с тулами
        response = self.llm.generate_with_tools(
            user_prompt=user_request,
            system_prompt=self._load_skill(skill),
            tools=tools_schema
        )

        # Если модель вызвала тулы
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # Выполняем тул
                if tool_name == "get_ticket":
                    ticket_data = self.ts_client.get_issue(tool_args["ticket_id"])
                    show_info(f"Получен тикет: {ticket_data['fields']['summary']}")
                    # Формируем контекст для генерации
                    context = f"Заголовок: {ticket_data['fields']['summary']}\nОписание: {ticket_data['fields']['description']}"
                    # Генерируем тест напрямую (без повторного обращения к модели с тулами)
                    test_code = self.generator.generate_test(
                        context=context,
                        skill_type=skill,
                        language=tool_args.get("language", self.config.get('DEFAULT_LANGUAGE', 'java')),
                        framework=tool_args.get("framework", self.config.get('DEFAULT_FRAMEWORK'))
                    )
                    return test_code
                elif tool_name == "generate_test":
                    # Если модель сама вызвала generate_test — возвращаем результат
                    return self.generator.generate_test(
                        context=tool_args["context"],
                        skill_type=tool_args.get("skill", skill),
                        language=tool_args.get("language", self.config.get('DEFAULT_LANGUAGE', 'java')),
                        framework=tool_args.get("framework", self.config.get('DEFAULT_FRAMEWORK'))
                    )
                elif tool_name == "save_to_file":
                    return save_to_file(tool_args["content"], tool_args["file_path"])
                elif tool_name == "open_editor":
                    return open_in_editor(tool_args["content"], tool_args["language"])
                else:
                    raise ValueError(f"Неизвестный тул: {tool_name}")
        else:
            # Если модель не вызвала тул — возвращаем её текстовый ответ
            return response.content

    def _load_skill(self, skill_name: str) -> str:
        skills_dir = Path(self.config.get('SKILLS_DIR', 'skills'))
        skill_file = skills_dir / f"{skill_name}.md"
        if skill_file.exists():
            return skill_file.read_text(encoding='utf-8')
        default_file = skills_dir / "default.md"
        if default_file.exists():
            return default_file.read_text(encoding='utf-8')
        return "Ты — эксперт по автоматизации тестирования. Генерируй качественный код."