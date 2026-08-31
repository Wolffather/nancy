from typing import Optional

class RequestBuilder:
    """Строит пользовательский запрос для агента на основе входных параметров."""

    @staticmethod
    def build(
        ticket_id: Optional[str] = None,
        description: Optional[str] = None,
        language: Optional[str] = None,
        framework: Optional[str] = None,
        skill: Optional[str] = None
    ) -> str:
        """
        Формирует запрос к агенту.
        Если передан ticket_id — запрос строится вокруг тикета.
        Иначе — вокруг текстового описания.
        """
        if ticket_id:
            parts = [f"Прочитай тикет {ticket_id} и сгенерируй тест"]
        else:
            parts = [f"Сгенерируй тест для: {description}"]

        if language:
            parts.append(f"на языке {language}")
        if framework:
            parts.append(f"с использованием фреймворка {framework}")
        if skill:
            parts.append(f"с использованием скилла {skill}")

        return ". ".join(parts)