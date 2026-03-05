from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ExtractedTicket(BaseModel):
    title: str
    description: str
    issue_type: str
    priority: str
    labels: List[str]

class JiraTicketSchema(BaseModel):
    slack_user_id: str
    jira_issue_key: str
    raw_text: str
    ai_summary: str
    status: str
    model_config = ConfigDict(from_attributes=True)
        