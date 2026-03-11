import pytest
import json
from app.services.slack_service import background_jira_logic

def test_background_jira_logic_flow(mocker):
    # 1. Mock the AI service to return a dummy ticket
    mock_ticket = mocker.Mock()
    mock_ticket.title = "AI Title"
    mock_ticket.description = "AI Description"
    mock_ticket.acceptance_criteria = "AI AC"
    mock_ticket.priority = "Medium"
    mock_ticket.issue_type = "Task"
    mock_ticket.labels = []
    
    mocker.patch("app.services.slack_service.ai_service.generate_full_ticket", return_value=mock_ticket)
    mocker.patch("app.services.slack_service.ai_service.check_for_duplicate", return_value=None)

    # 2. Mock Slack 'respond' and 'command'
    mock_respond = mocker.Mock()
    command = {"text": "Refactor auth"}

    # 3. Run logic
    background_jira_logic(command, mock_respond)

    # 4. Assertions
    args, _ = mock_respond.call_args
    blocks = args[0]["blocks"]
    
    # Verify the UI structure
    assert blocks[0]["text"]["text"] == "🪄 AI Ticket Expansion"
    # Check that the "Create Ticket" button contains the JSON-encoded data
    action_elements = blocks[5]["elements"]
    assert action_elements[0]["action_id"] == "confirm_create_action"
    
    # Verify JSON data inside the button value
    button_value = json.loads(action_elements[0]["value"])
    assert button_value["title"] == "AI Title"