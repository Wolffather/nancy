from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class Analyzer(ABC):
    """Базовый класс для анализаторов проектов."""

    def __init__(self, project_path: Path):
        self.project_path = project_path

    @abstractmethod
    def analyze(self) -> Dict[str, Any]:
        """
        Анализирует проект и возвращает структуру:
        {
            "language": "java",
            "classes": [
                {
                    "name": "UserService",
                    "package": "com.example",
                    "methods": [
                        {"name": "createUser", "params": [...], "return_type": "User", "annotations": [...]}
                    ]
                }
            ]
        }
        """
        pass

    @abstractmethod
    def get_dependencies(self) -> list:
        """Возвращает список зависимостей (для контекста)."""
        pass