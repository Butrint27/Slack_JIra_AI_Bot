import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .ai_service import ai_service
from .jira_service import jira_service
from ..db.session import SessionLocal
from ..db.models import JiraTicket

app = App(token=os.getenv("SLACK_BOT_TOKEN"))
JIRA_PROJECT = os.getenv("JIRA_PROJECT_KEY")

@app.command("/jira")
def handle_jira(ack, command, respond):
    ack()
    text, user = command["text"], command["user_id"]
    respond("🔍 AI is processing your ticket...")

    ticket = ai_service.process_message(text)
    issue = jira_service.create_issue(JIRA_PROJECT, ticket)

    if issue:
        with SessionLocal() as db:
            db.add(JiraTicket(slack_user_id=user, jira_issue_key=issue["key"], raw_text=text, ai_summary=ticket.title, status="created"))
            db.commit()
        respond(f"✅ Created: {os.getenv('JIRA_INSTANCE_URL')}/browse/{issue['key']}")
    else:
        respond("❌ Jira creation failed. Check bot logs.")

def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()