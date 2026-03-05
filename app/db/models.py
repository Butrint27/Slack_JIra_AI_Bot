from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
# Use absolute import to avoid "ImportError: attempted relative import with no known parent package"
from app.db.session import Base 

class JiraTicket(Base):
    __tablename__ = "jira_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    slack_user_id = Column(String, index=True) # Added index for faster searching
    jira_issue_key = Column(String, unique=True) # Issue keys should be unique
    raw_text = Column(String)
    ai_summary = Column(String)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    

