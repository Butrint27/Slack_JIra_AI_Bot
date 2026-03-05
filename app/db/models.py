from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base 

class BotConfig(Base):
    __tablename__ = "bot_configs"
    id = Column(Integer, primary_key=True, index=True)
    slack_team_id = Column(String, unique=True, index=True) 
    jira_project_key = Column(String, default="ENG")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class JiraTicket(Base):
    __tablename__ = "jira_tickets"
    id = Column(Integer, primary_key=True, index=True)
    slack_user_id = Column(String, index=True)
    jira_issue_key = Column(String, unique=True)
    raw_text = Column(String)
    ai_summary = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

