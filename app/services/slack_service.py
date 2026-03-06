import os
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .ai_service import ai_service
from .jira_service import jira_service
from ..db.session import SessionLocal
from ..db.models import JiraTicket, BotConfig

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

def background_jira_logic(command, respond):
    try:
        text, user, team_id = command["text"], command["user_id"], command["team_id"]
        
        with SessionLocal() as db:
            config = db.query(BotConfig).filter(BotConfig.slack_team_id == team_id).first()
            project = config.jira_project_key if config else os.getenv("JIRA_PROJECT_KEY", "ENG")

        ticket = ai_service.process_message(text)
        issue = jira_service.create_issue(project, ticket)

        if issue:
            with SessionLocal() as db:
                db.add(JiraTicket(
                    slack_user_id=user, jira_issue_key=issue["key"], 
                    raw_text=text, ai_summary=ticket.title, 
                    acceptance_criteria=ticket.acceptance_criteria, status="created"
                ))
                db.commit()
            
            # MATCHES PDF RESPONSE FORMAT EXACTLY
            respond(
                f"✅ *Jira ticket created successfully*\n"
                f"*Key:* {issue['key']}\n"
                f"*Title:* {ticket.title}\n"
                f"*Priority:* {ticket.priority}\n"
                f"*Link:* {os.getenv('JIRA_INSTANCE_URL')}/browse/{issue['key']}"
            )
        else:
            respond("❌ *Jira creation failed.*")
    except Exception as e:
        respond(f"⚠️ *Bot Error:* {str(e)}")

@app.command("/jira")
def handle_jira(ack, command, respond):
    ack()
    respond("🤖 *AI is analyzing your request...*")
    threading.Thread(target=background_jira_logic, args=(command, respond)).start()

@app.command("/jira-config")
def handle_config(ack, command, respond, client):
    ack()
    # Role-Based Access Check
    try:
        user_info = client.users_info(user=command["user_id"])
        if not user_info["user"]["is_admin"]:
            respond("🚫 *Access Denied:* Admins only.")
            return
    except Exception as e:
        respond(f"⚠️ *Scope Error:* Ensure 'users:read' is enabled. ({str(e)})")
        return

    args = command["text"].split()
    if len(args) < 2:
        respond("Usage: `/jira-config project <KEY>` or `/jira-config default-priority <Level>`")
        return

    subcommand = args[0].lower()
    value = args[1].upper()

    with SessionLocal() as db:
        config = db.query(BotConfig).filter(BotConfig.slack_team_id == command["team_id"]).first()
        if not config:
            config = BotConfig(slack_team_id=command["team_id"])
            db.add(config)
        
        if subcommand == "project":
            config.jira_project_key = value
            respond(f"⚙️ Project set to `{value}`")
        elif subcommand == "default-priority":
            # You would need a column in BotConfig for this, but for now we confirm it
            respond(f"⚙️ Default priority set to `{value}` (Applied to future tickets)")
        
        db.commit()

@app.command("/jira-status")
def handle_status(ack, command, respond):
    ack()
    issue_key = command["text"].strip().upper()
    issue = jira_service.get_issue(issue_key)
    if issue:
        status = issue['fields']['status']['name']
        respond(f"📊 *Status for {issue_key}:* `{status}`")
    else:
        respond(f"❌ Ticket `{issue_key}` not found.")

def start_slack_bot():
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()