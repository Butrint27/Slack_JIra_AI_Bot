import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .ai_service import ai_service
from .jira_service import jira_service
from ..db.session import SessionLocal
from ..db.models import JiraTicket

app = App(token=os.getenv("SLACK_BOT_TOKEN"))
JIRA_PROJECT = os.getenv("JIRA_PROJECT_KEY", "ENG")
JIRA_INSTANCE_URL = os.getenv("JIRA_INSTANCE_URL")

@app.command("/jira")
def handle_jira(ack, command, respond):
    ack()
    text = command["text"]
    user = command["user_id"]
    
    respond("🤖 *AI is analyzing your request...*")

    # 1. AI Extracts relevant fields [cite: 6, 22]
    ticket = ai_service.process_message(text)
    
    # 2. Create Jira ticket [cite: 7, 30]
    issue = jira_service.create_issue(JIRA_PROJECT, ticket)

    if issue:
        # Save to Database [cite: 73]
        with SessionLocal() as db:
            db_ticket = JiraTicket(
                slack_user_id=user,
                jira_issue_key=issue["key"],
                raw_text=text,
                ai_summary=ticket.title,
                status="created"
            )
            db.add(db_ticket)
            db.commit()

        # 3. Respond with the specific format required by the PDF [cite: 40, 41, 42, 45]
        issue_key = issue["key"]
        issue_link = f"{JIRA_INSTANCE_URL}/browse/{issue_key}"
        
        confirmation_text = (
            f"✅ *Jira ticket created successfully*\n\n"
            f"*Key:* {issue_key}\n"
            f"*Title:* {ticket.title}\n"
            f"*Priority:* {ticket.priority}\n"
            f"*Link:* {issue_link}"
        )
        respond(confirmation_text)
    else:
        respond("❌ *Failed to create Jira issue. Please check logs.*")

def start_slack_bot():
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    print("⚡ Slack bot is running and listening for /jira commands")
    handler.start()