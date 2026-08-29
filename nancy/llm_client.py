from openai import OpenAI


class LLMClient:
    def __init__(self, config):
        self.client = OpenAI(
            api_key=config['DEEPSEEK_API_KEY'],
            base_url="https://api.deepseek.com"
        )

    def generate(self, prompt, system=None):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3,
        )
        return response.choices[0].message.content