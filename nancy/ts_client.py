import os
import requests
from requests.auth import HTTPBasicAuth


def _mock_response(ticket_id):
    # Имитация ответа Jira REST API для тестового тикета
    return {
        "key": ticket_id,
        "fields": {
            "summary": f"Тестовый тикет {ticket_id}",
            "description": f"Это описание тестового тикета {ticket_id}. Требуется протестировать функциональность X."
        }
    }


class TSClient:
    def __init__(self, config, mock=False):
        self.mock = mock or config.get('MOCK_TS', False)
        if not self.mock:
            self.base_url = config['TS_URL']
            self.auth = HTTPBasicAuth(config['TS_EMAIL'], config['TS_API_TOKEN'])
        else:
            self.base_url = None
            self.auth = None

    def get_issue(self, ticket_id):
        if self.mock:
            return _mock_response(ticket_id)
        else:
            url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
            resp = requests.get(url, auth=self.auth)
            resp.raise_for_status()
            return resp.json()

