import os
import json
import requests
from ..db.schemas import ExtractedTicket

class AIService:
    def __init__(self):
        self.url = f"{os.getenv('OLLAMA_HOST')}/api/generate"
        self.model = os.getenv("OLLAMA_MODEL")

    def process_message(self, text: str) -> ExtractedTicket:
        # The prompt is now explicitly mapped to the 7 fields in the PDF
        prompt = (
            f"Context: You are a Jira AI assistant. Task: Extract these 7 fields from: '{text}'\n"
            f"1. title: Professional summary (5-8 words)\n"
            f"2. description: Full technical context\n"
            f"3. issue_type: 'Bug' if error/crash, else 'Task' or 'Story'\n"
            f"4. priority: 'Highest', 'High', 'Medium', 'Low', or 'Lowest'\n"
            f"5. labels: List of tags\n"
            f"6. components: List of affected areas\n"
            f"7. acceptance_criteria: List of requirements for completion\n"
            f"RETURN ONLY VALID JSON. NO PROSE."
        )
        try:
            resp = requests.post(self.url, json={
                "model": self.model, "prompt": prompt, "stream": False, "format": "json"
            }, timeout=45)
            
            data = json.loads(resp.json()["response"])
            return ExtractedTicket(**data)
        except Exception as e:
            # Fallback that still respects the 7-field schema
            return ExtractedTicket(
                title=text[:50], description=text, issue_type="Task", 
                priority="Medium", labels=["ai-fallback"], components=[], 
                acceptance_criteria="Manual review required."
            )

ai_service = AIService()