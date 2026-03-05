import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .ai_service import ai_service
from .jira_service import jira_service


SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
JIRA_PROJECT = os.getenv("JIRA_PROJECT_KEY", "ENG")


app = App(token=SLACK_BOT_TOKEN)


@app.command("/jira")
def jira_command(ack, command, respond):

    ack()

    text = command["text"]

    respond("🤖 AI is analyzing your message...")

    ticket = ai_service.process_message(text)

    issue = jira_service.create_issue(
        JIRA_PROJECT,
        ticket
    )

    if issue:

        respond(
            f"✅ Jira ticket created: {issue['key']}"
        )

    else:

        respond("❌ Failed to create Jira issue.")


def start_slack_bot():

    handler = SocketModeHandler(
        app,
        SLACK_APP_TOKEN
    )

    print("⚡ Slack bot running in Socket Mode")

    handler.start()