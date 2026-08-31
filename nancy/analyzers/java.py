import javalang
from pathlib import Path
from typing import Dict, Any, List
from .base import Analyzer

class JavaAnalyzer(Analyzer):
    def analyze(self) -> Dict[str, Any]:
        result = {
            "language": "java",
            "classes": [],
            "dependencies": self.get_dependencies()
        }

        # Рекурсивно обходим все .java файлы
        for java_file in self.project_path.rglob("*.java"):
            try:
                with open(java_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                tree = javalang.parse.parse(code)
                # Извлекаем классы и методы
                for path, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        class_info = self._parse_class(node)
                        result["classes"].append(class_info)
            except Exception as e:
                # Пропускаем файлы с ошибками парсинга
                continue

        return result

    def _parse_class(self, class_node):
        class_info = {
            "name": class_node.name,
            "package": self._get_package(class_node),
            "methods": []
        }
        for method in class_node.methods:
            method_info = {
                "name": method.name,
                "params": [
                    {"name": p.name, "type": p.type.name if p.type else "void"}
                    for p in method.parameters
                ],
                "return_type": method.return_type.name if method.return_type else "void",
                "annotations": [a.name for a in method.annotations] if method.annotations else []
            }
            class_info["methods"].append(method_info)
        return class_info

    def _get_package(self, class_node):
        # javalang не даёт простого доступа к пакету, можно хранить отдельно,
        # но для упрощения вернём пустую строку или имя папки
        return ""

    def get_dependencies(self) -> List[str]:
        # Можно парсить pom.xml или build.gradle (заглушка)
        pom = self.project_path / "pom.xml"
        if pom.exists():
            # Простой парсинг через xml.etree
            import xml.etree.ElementTree as ET
            try:
                tree = ET.parse(pom)
                root = tree.getroot()
                deps = []
                for dep in root.findall(".//dependency"):
                    group = dep.find("groupId")
                    artifact = dep.find("artifactId")
                    if group is not None and artifact is not None:
                        deps.append(f"{group.text}:{artifact.text}")
                return deps[:10]  # ограничим
            except:
                pass
        return []