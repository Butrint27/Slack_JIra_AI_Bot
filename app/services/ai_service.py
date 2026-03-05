import os
import json
import requests
from pydantic import BaseModel
from typing import List, Optional


class ExtractedTicket(BaseModel):

    title: str
    description: str
    issue_type: str
    priority: str
    labels: List[str]
    acceptance_criteria: Optional[str]


class AIService:

    def __init__(self):

        self.url = os.getenv(
            "OLLAMA_HOST",
            "http://ollama:11434"
        ) + "/api/generate"

        self.model = "tinyllama"

    def process_message(self, text: str):

        prompt = f"""
Extract Jira ticket information.

Message:
{text}

Return JSON with:
title
description
issue_type
priority
labels
acceptance_criteria
"""

        try:

            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=120
            )

            raw = response.json()["response"]

            data = json.loads(raw)

            return ExtractedTicket(**data)

        except Exception as e:

            print("AI error:", e)

            return ExtractedTicket(
                title=text[:50],
                description=text,
                issue_type="Task",
                priority="Medium",
                labels=["fallback"],
                acceptance_criteria=None
            )


ai_service = AIService()