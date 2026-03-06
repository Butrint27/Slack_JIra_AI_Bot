import os
import json
import threading
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from .ai_service import ai_service
from .jira_service import jira_service
from ..db.session import SessionLocal
from ..db.models import JiraTicket, BotConfig
from types import SimpleNamespace

app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# --- 1. PROPOSAL STAGE (Duplicate check + Buttons) ---
def background_jira_logic(command, respond):
    try:
        text, team_id = command["text"], command["team_id"]
        ticket = ai_service.process_message(text)
        
        duplicate = ai_service.check_for_duplicate(ticket.title)
        warning = f"⚠️ *Warning: Similar ticket exists ({duplicate.jira_issue_key})*\n" if duplicate else ""

        ticket_data = json.dumps({
            "title": ticket.title, "desc": ticket.description,
            "priority": ticket.priority, "type": ticket.issue_type,
            "ac": ticket.acceptance_criteria, "raw": text
        })

        respond({
            "blocks": [
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{warning}🤖 *AI Proposal*\n*Title:* {ticket.title}\n*Priority:* {ticket.priority}\n*Type:* {ticket.issue_type}"}},
                {"type": "actions", "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "✅ Confirm & Create"}, "style": "primary", "value": ticket_data, "action_id": "create_ticket"},
                    {"type": "button", "text": {"type": "plain_text", "text": "📝 Create as Task"}, "value": ticket_data, "action_id": "force_task"},
                    {"type": "button", "text": {"type": "plain_text", "text": "🗑️ Cancel"}, "style": "danger", "action_id": "cancel_ticket"}
                ]}
            ]
        })
    except Exception as e:
        respond(f"⚠️ *Analysis Error:* {str(e)}")

# --- 2. EXECUTION STAGE (Final Creation + PDF Response Format) ---
def process_final_creation(body, respond, override_type=None):
    data = json.loads(body["actions"][0]["value"])
    if override_type: data["type"] = override_type
    
    with SessionLocal() as db:
        config = db.query(BotConfig).filter(BotConfig.slack_team_id == body["team"]["id"]).first()
        project = config.jira_project_key if config else os.getenv("JIRA_PROJECT_KEY", "ENG")

    # Reconstruct ticket object for jira_service
    ticket_obj = SimpleNamespace(
        title=data["title"], description=data["desc"], 
        issue_type=data["type"], priority=data["priority"],
        labels=[], components=[], acceptance_criteria=data["ac"]
    )

    issue = jira_service.create_issue(project, ticket_obj)
    
    if issue:
        # SAVE TO DB for future duplicate checks
        with SessionLocal() as db:
            db.add(JiraTicket(
                slack_user_id=body["user"]["id"], jira_issue_key=issue["key"],
                raw_text=data["raw"], ai_summary=data["title"], status="created"
            ))
            db.commit()

        # THE EXACT FORMAT YOU REQUESTED:
        success_msg = (
            f"✅ *Jira ticket created successfully*\n"
            f"*Key:* {issue['key']}\n"
            f"*Title:* {data['title']}\n"
            f"*Priority:* {data['priority']}\n"
            f"*Link:* {os.getenv('JIRA_INSTANCE_URL')}/browse/{issue['key']}"
        )
        respond(success_msg, replace_original=True)
    else:
        respond("❌ *Jira creation failed.*", replace_original=True)

# --- ACTION HANDLERS ---
@app.action("create_ticket")
def handle_create(ack, body, respond):
    ack()
    process_final_creation(body, respond)

@app.action("force_task")
def handle_task(ack, body, respond):
    ack()
    process_final_creation(body, respond, override_type="Task")

@app.action("cancel_ticket")
def handle_cancel(ack, respond):
    ack()
    respond("🗑️ Ticket creation cancelled.", replace_original=True)

# --- SLASH COMMANDS ---
@app.command("/jira")
def handle_jira(ack, command, respond):
    ack()
    respond("🤖 *AI is analyzing your request...*")
    threading.Thread(target=background_jira_logic, args=(command, respond)).start()

@app.command("/jira-config")
def handle_config(ack, command, respond, client):
    ack()
    try:
        user_info = client.users_info(user=command["user_id"])
        if not user_info["user"]["is_admin"]:
            respond("🚫 *Access Denied:* Admins only.")
            return
    except Exception:
        respond("⚠️ *Error:* Bot lacks `users:read` scope.")
        return

    args = command["text"].split()
    if len(args) >= 2 and args[0].lower() == "project":
        val = args[1].upper()
        with SessionLocal() as db:
            cfg = db.query(BotConfig).filter(BotConfig.slack_team_id == command["team_id"]).first()
            if not cfg: 
                cfg = BotConfig(slack_team_id=command["team_id"])
                db.add(cfg)
            cfg.jira_project_key = val
            db.commit()
            respond(f"⚙️ Project set to `{val}`")
    else:
        respond("Usage: `/jira-config project <KEY>`")

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