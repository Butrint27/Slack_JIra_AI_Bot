# tests/test_jira_ticket.py
import pytest
from types import SimpleNamespace
from unittest.mock import patch
from app.services.jira_service import jira_service  # import the instance

@pytest.fixture
def sample_ticket():
    return SimpleNamespace(
        title="Testing pytest ticket",
        description="This ticket was automatically created by pytest.",
        issue_type="Task",
        priority="Medium",
        acceptance_criteria="1. Pytest should create this ticket.",
        labels=["pytest"],
        components=[]
    )

def test_create_jira_ticket_success(sample_ticket):
    project = "ENG"
    mock_issue = {"key": "ENG-123"}

    # Patch the 'create_issue' method of the JiraService instance
    with patch("app.services.jira_service.jira_service.create_issue", return_value=mock_issue) as mock_create:
        issue = jira_service.create_issue(project, sample_ticket)

        mock_create.assert_called_once_with(project, sample_ticket)
        assert issue is not None
        assert issue["key"] == "ENG-123"

def test_create_jira_ticket_failure(sample_ticket):
    project = "ENG"

    with patch("app.services.jira_service.jira_service.create_issue", side_effect=Exception("Jira API error")) as mock_create:
        with pytest.raises(Exception) as exc:
            jira_service.create_issue(project, sample_ticket)

        mock_create.assert_called_once_with(project, sample_ticket)
        assert "Jira API error" in str(exc.value)

def test_create_jira_ticket_missing_fields():
    project = "ENG"
    incomplete_ticket = SimpleNamespace(
        title="", description="", issue_type="", priority="", acceptance_criteria="",
        labels=[], components=[]
    )
    mock_issue = {"key": "ENG-999"}

    with patch("app.services.jira_service.jira_service.create_issue", return_value=mock_issue) as mock_create:
        issue = jira_service.create_issue(project, incomplete_ticket)

        mock_create.assert_called_once_with(project, incomplete_ticket)
        assert issue["key"] == "ENG-999"
    
   