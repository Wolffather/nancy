# Nancy — AI-агент для автоматизации тестирования

**Nancy** — это CLI-агент на Python, который генерирует автотесты на основе текстового описания или тикета из трекинг-системы. Использует DeepSeek (или другую LLM) для написания кода на Java, Python, JavaScript, C#, Go, Ruby с кастомизируемыми скиллами.

---

## 📌 Состояние проекта: MVP

- ✅ CLI с интерактивным режимом
- ✅ Генерация тестов по описанию или тикету
- ✅ Поддержка 6 языков
- ✅ Система скиллов (кастомные промпты)
- ✅ Управление настройками через CLI
- ✅ Мок-режим для работы без трекинг-системы
- ✅ Сохранение в файл
- ❌ RAG (векторный поиск по требованиям)
- ❌ LLM-as-a-Judge (автопроверка тестов)
- ❌ Интеграция с реальной Jira/YouTrack

---

## 📦 Требования

- Python 3.11 или выше
- DeepSeek API-ключ (или другой OpenAI-совместимый API)
- Опционально: Docker

---

## ⚙️ Установка и настройка

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/Wolffather/nancy.git
cd nancy-agent
```

### 2. Создайте и активируйте виртуальное окружение
### Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (cmd):
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установите зависимости и саму утилиту
```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Настройте переменные окружения
```bash
cp .env_example .env
```

### Отредактируйте .env, добавьте DEEPSEEK_API_KEY=sk-...

### 5. Проверьте установку
```bash
nancy --help
```