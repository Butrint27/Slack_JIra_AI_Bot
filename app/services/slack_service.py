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

# --- 1. CORE GENERATION & CREATION LOGIC ---

def background_jira_logic(command, respond):
    try:
        title_text = command["text"]
        if not title_text:
            respond("⚠️ Please provide a title. Usage: `/jira [Ticket Title]`")
            return

        # Let AI expand the title into a full ticket
        ticket = ai_service.generate_full_ticket(title_text)
        
        duplicate = ai_service.check_for_duplicate(ticket.title)
        warning = f"⚠️ *Duplicate Alert ({duplicate.jira_issue_key})*\n" if duplicate else ""
        
        # Package the generated data for the confirmation button
        ticket_data = json.dumps({
            "title": ticket.title, 
            "desc": ticket.description, 
            "priority": ticket.priority, 
            "type": ticket.issue_type, 
            "ac": ticket.acceptance_criteria,
            "labels": ticket.labels
        })
        
        # Enhanced preview blocks for generated content
        respond({
            "blocks": [
                {"type": "header", "text": {"type": "plain_text", "text": "🪄 AI Ticket Expansion"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"{warning}*Proposed Title:* {ticket.title}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*AI Description:*\n{ticket.description}"}},
                {"type": "section", "text": {"type": "mrkdwn", "text": f"*Acceptance Criteria:*\n{ticket.acceptance_criteria}"}},
                {"type": "context", "elements": [
                    {"type": "mrkdwn", "text": f"⚡ *Priority:* {ticket.priority}  |  🏷️ *Type:* {ticket.issue_type}"}
                ]},
                {"type": "actions", "elements": [
                    {"type": "button", "text": {"type": "plain_text", "text": "✅ Create Ticket"}, "style": "primary", "value": ticket_data, "action_id": "confirm_create_action"},
                    {"type": "button", "text": {"type": "plain_text", "text": "🗑️ Discard"}, "style": "danger", "action_id": "cancel_action"}
                ]}
            ]
        })
    except Exception as e:
        respond(f"❌ *AI Generation Error:* {str(e)}")

@app.command("/jira")
def handle_jira(ack, command, respond):
    ack()
    respond("🤖 Thinking... Generating technical details with Ollama...")
    threading.Thread(target=background_jira_logic, args=(command, respond)).start()

@app.action("confirm_create_action")
def handle_confirm_create(ack, body, respond):
    ack()
    data = json.loads(body["actions"][0]["value"])
    
    ticket_obj = SimpleNamespace(
        title=data["title"], 
        description=data["desc"],
        issue_type=data["type"], 
        priority=data["priority"],
        acceptance_criteria=data["ac"],
        labels=data.get("labels", []),
        components=[]
    )

    with SessionLocal() as db:
        config = db.query(BotConfig).filter(BotConfig.slack_team_id == body["team"]["id"]).first()
        project = config.jira_project_key if config else os.getenv("JIRA_PROJECT_KEY", "ENG")

    issue = jira_service.create_issue(project, ticket_obj)
    
    if issue:
        with SessionLocal() as db:
            db.add(JiraTicket(
                slack_user_id=body["user"]["id"], 
                jira_issue_key=issue["key"],
                raw_text=data["title"], 
                ai_summary=data["title"], 
                status="created"
            ))
            db.commit()
        respond(f"✅ *Ticket {issue['key']} created!*\nLink: {os.getenv('JIRA_INSTANCE_URL')}/browse/{issue['key']}", replace_original=True)
    else:
        respond("❌ Failed to create ticket in Jira. Check API logs.", replace_original=True)

# --- 2. STATUS & UPDATE LOGIC ---

@app.command("/jira-status")
def handle_status(ack, command, respond):
    ack()
    key = command["text"].strip().upper()
    issue = jira_service.get_issue(key)
    
    if not issue:
        return respond(f"❌ Ticket `{key}` not found.")

    fields = issue.get('fields', {})
    status = fields.get('status', {}).get('name', 'Unknown')
    priority = fields.get('priority', {}).get('name', 'None')
    
    respond(f"📊 *Status for {key}:*\n*Summary:* {fields.get('summary')}\n*Status:* `{status}`\n*Priority:* `{priority}`")

@app.command("/jira-update")
def handle_update(ack, command, respond):
    ack()
    args = command["text"].split()
    if len(args) < 2: return respond("Usage: `/jira-update <KEY> <Priority>`")

    key, raw_prio = args[0].upper(), args[1].lower()
    mapping = {"height": "Highest", "highest": "Highest", "high": "High", "medium": "Medium", "low": "Low"}
    new_priority = mapping.get(raw_prio, raw_prio.capitalize())

    if jira_service.update_issue(key, {"priority": {"name": new_priority}}):
        respond(f"✅ Priority for *{key}* updated to *{new_priority}*.")
    else:
        respond(f"❌ Failed to update *{key}*.")

# --- 3. MOVE & DELETE LOGIC ---

@app.command("/jira-move")
def handle_move(ack, command, respond):
    ack()
    args = command["text"].split()
    if len(args) < 2: return respond("Usage: `/jira-move <KEY> <Status>`")
    
    key, status_input = args[0].upper(), " ".join(args[1:]).lower()
    transitions = jira_service.get_available_transitions(key)
    t_id = next((t['id'] for t in transitions if status_input in t['name'].lower()), None)
    
    if t_id and jira_service.transition_issue(key, t_id):
        respond(f"🚀 *{key}* moved to *{status_input.title()}*")
    else:
        avail = ", ".join([f"`{t['name']}`" for t in transitions])
        respond(f"❌ Move failed. Available moves: {avail}")

@app.command("/jira-delete")
def handle_delete_command(ack, command, respond):
    ack()
    key = command["text"].strip().upper()
    if not key: return respond("Usage: `/jira-delete <KEY>`")

    respond({
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": f"❓ *Confirm deletion of {key}?*"}},
            {"type": "actions", "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "Yes, Delete"}, "style": "danger", "value": key, "action_id": "confirm_delete_action"},
                {"type": "button", "text": {"type": "plain_text", "text": "Cancel"}, "action_id": "cancel_action"}
            ]}
        ]
    })

@app.action("confirm_delete_action")
def handle_confirm_delete(ack, body, respond):
    ack()
    key = body["actions"][0]["value"]
    if jira_service.delete_issue(key):
        respond(f"🗑️ *{key}* deleted permanently.", replace_original=True)
    else:
        respond(f"❌ Failed to delete *{key}*. (Permission Denied).", replace_original=True)

@app.action("cancel_action")
def handle_cancel(ack, respond):
    ack()
    respond("🗑️ Action cancelled/proposal discarded.", replace_original=True)

def start_slack_bot():
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()