import requests
from requests.auth import HTTPBasicAuth


class TSClient:
    def __init__(self, config):
        self.base_url = config['JIRA_URL']
        self.auth = HTTPBasicAuth(config['JIRA_EMAIL'], config['JIRA_API_TOKEN'])

    def get_issue(self, ticket_id):
        url = f"{self.base_url}/rest/api/3/issue/{ticket_id}"
        resp = requests.get(url, auth=self.auth)
        resp.raise_for_status()
        return resp.json()