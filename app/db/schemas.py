# build a schema using pydantic
from pydantic import BaseModel, ConfigDict

class BotConfigSchema(BaseModel):
    slack_team_id: str
    jira_project_key: str
    default_priority: str
    
    # New Pydantic V2 way to handle ORM mapping
    model_config = ConfigDict(from_attributes=True)

class JiraTicketSchema(BaseModel):
    slack_user_id: str
    jira_issue_key: str
    raw_text: str
    ai_summary: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)
        