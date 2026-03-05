import os
import json
import requests
from requests.auth import HTTPBasicAuth


class JiraService:

    def __init__(self):

        self.url = os.getenv("JIRA_INSTANCE_URL")

        self.email = os.getenv("JIRA_USER_EMAIL")

        self.token = os.getenv("JIRA_API_TOKEN")

        self.auth = HTTPBasicAuth(self.email, self.token)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_issue(self, project_key, ticket):

        endpoint = f"{self.url}/rest/api/3/issue"

        description = {
            "version": 1,
            "type": "doc",
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": ticket.description
                        }
                    ]
                }
            ]
        }

        payload = {
            "fields": {

                "project": {"key": project_key},

                "summary": ticket.title,

                "description": description,

                "issuetype": {
                    "name": ticket.issue_type
                },

                "priority": {
                    "name": ticket.priority
                },

                "labels": ticket.labels
            }
        }

        response = requests.post(
            endpoint,
            data=json.dumps(payload),
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 201:

            return response.json()

        print("Jira error:", response.text)

        return None


jira_service = JiraService()