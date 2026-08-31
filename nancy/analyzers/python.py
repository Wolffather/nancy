import ast
from pathlib import Path
from typing import Dict, Any, List
from .base import Analyzer

class PythonAnalyzer(Analyzer):
    def analyze(self) -> Dict[str, Any]:
        result = {
            "language": "python",
            "classes": [],
            "dependencies": self.get_dependencies()
        }

        for py_file in self.project_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_info = self._parse_class(node)
                        result["classes"].append(class_info)
            except Exception:
                continue
        return result

    def _parse_class(self, class_node):
        class_info = {
            "name": class_node.name,
            "methods": []
        }
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = {
                    "name": item.name,
                    "params": [arg.arg for arg in item.args.args if arg.arg != "self"],
                    "return_type": "Any",  # можно попытаться из аннотации
                }
                class_info["methods"].append(method_info)
        return class_info

    def get_dependencies(self) -> List[str]:
        req = self.project_path / "requirements.txt"
        if req.exists():
            with open(req, 'r') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return []