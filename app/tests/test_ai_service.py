import pytest
from app.services.ai_service import AIService

def test_generate_full_ticket_success(mocker):
    # Mock the requests.post call to Ollama
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"title": "Test Task", "description": "Detailed desc", "issue_type": "Bug", "priority": "High", "acceptance_criteria": "1. Done"}'
    }
    mocker.patch("requests.post", return_value=mock_response)

    service = AIService()
    result = service.generate_full_ticket("Fix login")

    assert result.title == "Test Task"
    assert result.priority == "High"
    assert isinstance(result.labels, list)

def test_generate_full_ticket_fallback_on_failure(mocker):
    # Simulate a 500 error or timeout
    mocker.patch("requests.post", side_effect=Exception("Ollama Down"))

    service = AIService()
    result = service.generate_full_ticket("Fix login")

    # Should return the fallback ticket defined in your 'except' block
    assert result.description == "Error in AI generation logic."
    assert "error" in result.labels