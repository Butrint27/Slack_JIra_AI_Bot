from pydantic import BaseModel, ConfigDict

class JiraTicketSchema(BaseModel):
    slack_user_id: str
    jira_issue_key: str
    raw_text: str
    ai_summary: str
    status: str
    model_config = ConfigDict(from_attributes=True)
        