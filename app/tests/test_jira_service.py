import pytest
from app.services.jira_service import JiraService
from types import SimpleNamespace

@pytest.fixture
def jira_service():
    return JiraService()

def test_create_issue_payload(mocker, jira_service):
    mock_post = mocker.patch("requests.post")
    mock_post.return_value.status_code = 201
    mock_post.return_value.json.return_value = {"key": "PROJ-123"}

    mock_ticket = SimpleNamespace(
        title="Test Title",
        description="Test Desc",
        issue_type="Task",
        priority="Medium",
        acceptance_criteria="AC1",
        labels=["test"],
        components=["Backend"]
    )

    result = jira_service.create_issue("ENG", mock_ticket)

    assert result["key"] == "PROJ-123"
    # Check if the description was formatted into the Atlassian 'doc' structure
    args, kwargs = mock_post.call_args
    assert kwargs['json']['fields']['project']['key'] == "ENG"
    assert kwargs['json']['fields']['description']['type'] == "doc"

def test_get_issue_not_found(mocker, jira_service):
    mock_get = mocker.patch("requests.get")
    mock_get.return_value.status_code = 404
    
    result = jira_service.get_issue("INVALID-1")
    assert result is None