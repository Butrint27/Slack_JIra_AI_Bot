import threading
from fastapi import FastAPI

from .db.session import engine
from .db import models
from .services.slack_service import start_slack_bot


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Jira AI Bot")


@app.on_event("startup")
def startup():

    thread = threading.Thread(
        target=start_slack_bot,
        daemon=True
    )

    thread.start()

    print("Slack bot thread started")


@app.get("/")
def root():

    return {"status": "running"}


@app.get("/health")
def health():

    return {"status": "healthy"}