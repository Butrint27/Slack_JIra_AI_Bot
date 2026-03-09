import os
import requests
from requests.auth import HTTPBasicAuth

class JiraService:
    def __init__(self):
        self.url = os.getenv("JIRA_INSTANCE_URL")
        self.auth = HTTPBasicAuth(os.getenv("JIRA_USER_EMAIL"), os.getenv("JIRA_API_TOKEN"))
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def create_issue(self, project_key, ticket):
        """Creates a new Jira issue and returns the JSON response."""
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
                "labels": ticket.labels if hasattr(ticket, 'labels') else [],
                "components": [{"name": c} for c in ticket.components] if hasattr(ticket, 'components') else []
            }
        }
        res = requests.post(endpoint, json=payload, headers=self.headers, auth=self.auth)
        return res.json() if res.status_code == 201 else None

    def get_issue(self, issue_key):
        """Fetches details for a specific issue key."""
        res = requests.get(f"{self.url}/rest/api/3/issue/{issue_key}", headers=self.headers, auth=self.auth)
        return res.json() if res.status_code == 200 else None

    def update_issue(self, issue_key, fields):
        """Updates fields (Priority, Summary, etc). Returns True if successful."""
        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}"
        res = requests.put(endpoint, json={"fields": fields}, headers=self.headers, auth=self.auth)
        return res.status_code == 204

    def delete_issue(self, issue_key):
        """Deletes an issue. Returns True if 204 (No Content)."""
        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}"
        res = requests.delete(endpoint, headers=self.headers, auth=self.auth)
        return res.status_code == 204

    def get_available_transitions(self, issue_key):
        """Gets all possible status moves (To Do -> Done, etc)."""
        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}/transitions"
        res = requests.get(endpoint, headers=self.headers, auth=self.auth)
        return res.json().get("transitions", []) if res.status_code == 200 else []

    def transition_issue(self, issue_key, transition_id):
        """Executes a status move using a transition ID."""
        endpoint = f"{self.url}/rest/api/3/issue/{issue_key}/transitions"
        payload = {"transition": {"id": transition_id}}
        res = requests.post(endpoint, json=payload, headers=self.headers, auth=self.auth)
        return res.status_code == 204

jira_service = JiraService()