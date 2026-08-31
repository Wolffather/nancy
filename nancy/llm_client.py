import json
from openai import OpenAI


class LLMClient:
    def __init__(self, config):
        self.api_key = config['LLM_API_KEY']
        self.base_url = config['LLM_BASE_URL']
        self.model = config['LLM_MODEL']
        self.temperature = config['LLM_TEMPERATURE']

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate(self, user_prompt, system_prompt=None):
        """Простая генерация без тулов (для обратной совместимости)."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    def generate_with_tools(self, user_prompt, system_prompt=None, tools=None):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or [],
            tool_choice="auto",
            temperature=self.temperature,
        )
        return response.choices[0].message