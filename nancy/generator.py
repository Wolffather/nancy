from pathlib import Path


class TestGenerator:
    def __init__(self, llm_client, ts_client, skills_dir="skills"):
        self.llm = llm_client
        self.jira = ts_client
        self.skills_dir = Path(skills_dir)

    def generate_test(self, context, skill_type="api", language="java", framework=None):
        system_prompt = self._load_skill(skill_type)

        # Строим пользовательский промпт
        user_prompt = f"Сгенерируй автотест на языке {language}"
        if framework:
            user_prompt += f" с использованием фреймворка {framework}"
        else:
            # Если фреймворк не указан, подбираем по языку
            default_frameworks = {
                "java": "JUnit 5 и RestAssured",
                "python": "pytest и requests",
                "javascript": "Jest и supertest",
            }
            user_prompt += f" с использованием {default_frameworks.get(language.lower(), 'подходящего фреймворка')}"

        user_prompt += f"\n\nОписание сценария:\n{context}"

        # Добавляем дополнительные указания в зависимости от языка
        if language.lower() == "java":
            user_prompt += "\n\nИспользуй стандартную структуру: import, класс, тестовый метод. Проверяй статус-код и поля JSON."
        elif language.lower() == "python":
            user_prompt += "\n\nИспользуй фикстуры, ассерты из pytest. Проверяй статус-код и JSON."
        elif language.lower() == "javascript":
            user_prompt += "\n\nИспользуй describe/it, асинхронные запросы. Проверяй статус-код и тело ответа."

        return self.llm.generate(user_prompt, system_prompt)

    def _load_skill(self, skill_type):
        # Ищем файл skills/<skill_type>.md
        skill_file = self.skills_dir / f"{skill_type}.md"
        if skill_file.exists():
            return skill_file.read_text(encoding="utf-8")
        # Если не найден, пробуем default.md
        default_file = self.skills_dir / "default.md"
        if default_file.exists():
            return default_file.read_text(encoding="utf-8")
        # Если и default нет — жёсткий fallback
        return "Ты — эксперт по автоматизации тестирования. Генерируй качественный код на Java."