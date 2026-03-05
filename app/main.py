import threading
from fastapi import FastAPI
from .db import models
from .services.slack_service import start_slack_bot
from .db.session import engine, wait_for_db

app = FastAPI(title="Jira AI Bot [cite: 1]")

@app.on_event("startup")
def startup():
    if wait_for_db():
        # Create all tables on startup [cite: 73]
        models.Base.metadata.create_all(bind=engine)
        # Start Slack Socket Mode in background [cite: 70, 85]
        threading.Thread(target=start_slack_bot, daemon=True).start()
        print("🚀 Systems Online: FastAPI + Slack Bot")

@app.get("/health")
def health():
    return {"status": "healthy"}