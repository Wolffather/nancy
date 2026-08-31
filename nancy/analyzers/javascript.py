from pathlib import Path
from typing import Dict, Any, List
from .base import Analyzer

class JavaScriptAnalyzer(Analyzer):
    def analyze(self) -> Dict[str, Any]:
        # Пока просто возвращаем пустую структуру
        return {"language": "javascript", "classes": [], "dependencies": self.get_dependencies()}

    def get_dependencies(self) -> List[str]:
        pkg = self.project_path / "package.json"
        if pkg.exists():
            import json
            with open(pkg, 'r') as f:
                data = json.load(f)
                return list(data.get("dependencies", {}).keys())
        return []