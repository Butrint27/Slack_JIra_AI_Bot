from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from pydantic import BaseModel, ConfigDict
from .session import Base

# --- SQLAlchemy Models (Database Tables) ---

class BotConfig(Base):
    __tablename__ = 'bot_configs'
    
    id = Column(Integer, primary_key=True, index=True)
    slack_team_id = Column(String, unique=True, index=True)
    jira_project_key = Column(String)
    default_priority = Column(String)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

class JiraTicket(Base):
    __tablename__ = 'jira_tickets'
    
    id = Column(Integer, primary_key=True, index=True)
    slack_user_id = Column(String)
    jira_issue_key = Column(String)
    raw_text = Column(String)
    ai_summary = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

