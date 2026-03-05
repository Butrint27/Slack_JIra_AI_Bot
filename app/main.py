import threading
from fastapi import FastAPI
from .db import models
from .services.slack_service import start_slack_bot
from .db.session import engine, wait_for_db

app = FastAPI()

@app.on_event("startup")
def startup():
    if wait_for_db():
        models.Base.metadata.create_all(bind=engine)
        threading.Thread(target=start_slack_bot, daemon=True).start()
        print("🚀 Systems Online")

@app.get("/health")
def health(): return {"status": "ok"}