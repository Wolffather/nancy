# nancy/tools.py
_registered_tools = []

def register_tool(name, description, parameters):
    _registered_tools.append({
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": list(parameters.keys())
            }
        }
    })

def get_tools_schema():
    return _registered_tools

# Регистрируем тулы
register_tool(
    name="get_ticket",
    description="Получить тикет из трекинг-системы по ID.",
    parameters={
        "ticket_id": {"type": "string", "description": "ID тикета"}
    }
)
register_tool(
    name="generate_test",
    description="Сгенерировать автотест по описанию.",
    parameters={
        "context": {"type": "string", "description": "Описание сценария"},
        "language": {"type": "string", "description": "Язык программирования"},
        "framework": {"type": "string", "description": "Фреймворк"},
        "skill": {"type": "string", "description": "Тип скилла"}
    }
)
register_tool(
    name="save_to_file",
    description="Сохранить код в файл.",
    parameters={
        "content": {"type": "string", "description": "Содержимое"},
        "file_path": {"type": "string", "description": "Путь к файлу"}
    }
)
register_tool(
    name="open_editor",
    description="Открыть редактор для ручного редактирования.",
    parameters={
        "content": {"type": "string", "description": "Текст для редактирования"},
        "language": {"type": "string", "description": "Язык"}
    }
)
register_tool(
    name="analyze_project",
    description="Анализирует проект по указанному пути, находит классы и методы, возвращает структуру для генерации тестов.",
    parameters={
        "project_path": {"type": "string", "description": "Путь к корню проекта"},
        "language": {"type": "string", "description": "Язык проекта (java, python...)"},
        "test_framework": {"type": "string", "description": "Фреймворк для генерации тестов"}
    }
)