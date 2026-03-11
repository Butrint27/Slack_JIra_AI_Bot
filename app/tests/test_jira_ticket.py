import os
from types import SimpleNamespace
from app.services.jira_service import jira_service


def test_create_jira_ticket():
    project = os.getenv("JIRA_PROJECT_KEY", "ENG")

    ticket = SimpleNamespace(
        title="Testing pytest ticket",
        description="This ticket was automatically created by pytest.",
        issue_type="Task",
        priority="Medium",
        acceptance_criteria="1. Pytest should create this ticket.",
        labels=["pytest"],
        components=[]
    )

    issue = jira_service.create_issue(project, ticket)

    assert issue is not None
    assert "key" in issue

    print(f"Jira ticket created: {issue['key']}")