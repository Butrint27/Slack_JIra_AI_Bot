import os
import requests
from requests.auth import HTTPBasicAuth
from ..db.schemas import ExtractedTicket

class JiraService:
    def __init__(self):
        self.url = os.getenv("JIRA_INSTANCE_URL")
        self.auth = HTTPBasicAuth(os.getenv("JIRA_USER_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def create_issue(self, project_key, ticket: ExtractedTicket):
        endpoint = f"{self.url}/rest/api/3/issue"
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": ticket.title,
                "description": {
                    "version": 1, "type": "doc",
                    "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": ticket.description}]},
                        {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Acceptance Criteria"}]},
                        {"type": "paragraph", "content": [{"type": "text", "text": ticket.acceptance_criteria}]}
                    ]
                },
                "issuetype": {"name": ticket.issue_type},
                "priority": {"name": ticket.priority},
                "labels": ticket.labels,
                "components": [{"name": c} for c in ticket.components]
            }
        }
        res = requests.post(endpoint, json=payload, headers=self.headers, auth=self.auth)
        print(f"Jira API Response: {res.status_code} - {res.text}") # PDF Requirement: Log Jira responses
        return res.json() if res.status_code == 201 else None

    def get_issue(self, issue_key):
        res = requests.get(f"{self.url}/rest/api/3/issue/{issue_key}", headers=self.headers, auth=self.auth)
        return res.json() if res.status_code == 200 else None

jira_service = JiraService()