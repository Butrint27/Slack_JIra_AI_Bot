import os
import json
import requests
import re
from datetime import datetime, timedelta
from ..db.schemas import ExtractedTicket
from ..db.models import JiraTicket
from ..db.session import SessionLocal

class AIService:
    def __init__(self):
        self.url = f"{os.getenv('OLLAMA_HOST')}/api/generate"
        self.model = os.getenv("OLLAMA_MODEL")

    def generate_full_ticket(self, title: str) -> ExtractedTicket:
        # Simplified prompt: Less talk, more structure
        prompt = (
            f"Write a Jira ticket JSON for: '{title}'.\n"
            f"Keys: title, description, issue_type, priority, labels, components, acceptance_criteria.\n"
            f"Description must be a detailed technical paragraph.\n"
            f"Acceptance criteria must be a numbered list."
        )
        
        try:
            # We use 'format': 'json' which forces Ollama to output valid JSON
            resp = requests.post(self.url, json={
                "model": self.model, 
                "prompt": prompt, 
                "stream": False, 
                "format": "json" 
            }, timeout=90)
            
            raw_response = resp.json().get("response", "{}")
            data = json.loads(raw_response)
            
            # --- AGGRESSIVE CLEANING ---
            # This maps whatever the AI gives us to exactly what your Pydantic model needs
            refined_data = {
                "title": str(data.get("title", title)),
                "description": str(data.get("description", "Needs technical overview.")),
                "issue_type": str(data.get("issue_type", "Task")),
                "priority": str(data.get("priority", "Medium")),
                "labels": data.get("labels") if isinstance(data.get("labels"), list) else [],
                "components": data.get("components") if isinstance(data.get("components"), list) else [],
                "acceptance_criteria": str(data.get("acceptance_criteria", "1. Complete task."))
            }
            
            return ExtractedTicket(**refined_data)
            
        except Exception as e:
            # Log the actual error to your terminal so we can see it!
            print(f"DEBUG: Ollama raw response was: {raw_response if 'raw_response' in locals() else 'No Response'}")
            print(f"⚠️ AI Generation Error: {str(e)}")
            
            return ExtractedTicket(
                title=title, 
                description="Error in AI generation logic.",
                issue_type="Task", 
                priority="Medium", 
                labels=["error"], 
                components=[],
                acceptance_criteria="1. Verify manually."
            )

    def check_for_duplicate(self, title: str):
        with SessionLocal() as db:
            yesterday = datetime.utcnow() - timedelta(days=1)
            return db.query(JiraTicket).filter(
                JiraTicket.ai_summary.ilike(f"%{title[:15]}%"),
                JiraTicket.created_at >= yesterday
            ).first()

ai_service = AIService()