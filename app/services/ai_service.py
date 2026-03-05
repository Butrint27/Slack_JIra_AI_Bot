import os
import json
import requests
from pydantic import BaseModel
from typing import List

class ExtractedTicket(BaseModel):
    title: str
    description: str
    issue_type: str
    priority: str
    labels: List[str]

class AIService:
    def __init__(self):
        self.url = os.getenv("OLLAMA_HOST") + "/api/generate"
        self.model = os.getenv("OLLAMA_MODEL")

    def process_message(self, text: str):
        prompt = f"Convert this to JSON with keys (title, description, issue_type, priority, labels): {text}"
        try:
            resp = requests.post(self.url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=30)
            data = json.loads(resp.json()["response"])
            return ExtractedTicket(**data)
        except Exception as e:
            print(f"AI Fallback triggered: {e}")
            return ExtractedTicket(title=text[:50], description=text, issue_type="Task", priority="Medium", labels=["bot"])

ai_service = AIService()