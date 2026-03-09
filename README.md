🤖 Jira Slack Bot
________________________________________________________________________________________________

This project is a Slack bot that integrates with Jira to manage tasks, bugs, stories, and epics. It allows users to create and manage tickets directly from Slack.

💬 Sample Slack Conversation
________________________________________________________________________________________________

The following is an example of how to use the AI Bot to create a jira ticket using Slack:

/jira Hello this is the first test example

Jira ticket created successfully
Key: ENG-25
Title: Hello this is the first test example
Priority: Medium
Link: https://butrintbajrami8.atlassian.net/browse/ENG-25

🚀 Features
________________________________________________________________________________________________

The bot supports the following commands:
  1. /jira <title> - Create a new jira ticket from Slack
  2. /jira-status <ENG-{id}> - Check the status of the key specificly the current board 
  3. /jira-config project <title> - Admin only can change the project key 

🏁 Getting Started
________________________________________________________________________________________________

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes

📋 Prerequisites
________________________________________________________________________________________________

  1. Python3
  2. pip

🔧 Installing
________________________________________________________________________________________________

  1. Clone the repository
  2. Install the dependecies with pip:
  3. Use Docker to run this project
  4. Use images such as ollama(tinyllama), postgresql, python3

  pip install -r requirements.txt

  5. Run the application

  docker-compose up --build -d

🛠️ Built With
________________________________________________________________________________________________

  1. Python3
  2. FastAPI
  3. Slack Bolt SDK
  4. Atlassian REST API v3

🤝 Integrating with Slack
________________________________________________________________________________________________

🤖 Creating a Slack Bot

To create a Slack bot, follow these steps:

  1. Go to the Slack API webiste and click on the "Create New App" button.
  2. In the pop-up window, select 'From scratch', give your app a name, and select the workspace where you want to install the bot.
  3. Go to the "Slash Commands" in order to prepare the commands need it such as '/jira', '/jira-config', '/jira-status'
  4. In the "OAuth & Permissions" you need to add the scopes first such as 'chat:write', 'commands', 'files:read', 'team:read', 'users:read' once you do that install the workspace and copy the 'xoxb' token which is 'SLACK_BOT_TOKEN' you might gona have to save it on a .env for better code
  5. For this project you dont need a tool such as ngrok but instead you can use Slack Websocket which you can find in the left pannel 'Socket Mode' simply enable it for a easy communication
  6. You might have to add the 'xapp' token for the 'SLACK_APP_TOKEN' just make sure you place it on a normal notepad to save it the location of this one is on the 'Socket Token (Slack-Socket Mode)'

📚 Project Structure
________________________________________________________________________________________________

Use the 'app' folder where it will go all the work where there will be inlcuded these folders 'db', 'services' and there will be the 'main.py'

In the 'db' folder we have classes such as 'models.py', 'schemas.py', 'session.py' and make sure you include '__init__.py'

In the 'services' folder there will be classes such as 'ai_service.py', 'jira_service.py', 'slack_service.py' and of course the '__init__.py'

Outside of the 'app' folder there are neccesary files such as '.gitattributes', '.gitignore', 'docker-compose.yml', 'Dockerfile', 'requirements.txt' and 'README.md'

⚙️ Configuration
________________________________________________________________________________________________

This project uses a .env file for configuration. This file should be located at the root of the project and should not be checked into version control. It is used to store sensitive information such as API keys, database credentials, and other environment-specific settings.

Here's a sample .env file:

DATABASE_URL=your-db-connection

SLACK_BOT_TOKEN=your-slack-bot-token
SLACK_APP_TOKEN=your-slack-app-token

OLLAMA_MODEL=tinyllama
OLLAMA_HOST=http://ollama:11434

JIRA_API_TOKEN=your-jira-api-token
JIRA_INSTANCE_URL=your-jira-url
JIRA_USER_EMAIL=your-jira-email
JIRA_PROJECT_KEY=your-jira-project-key

Replace the placeholders with the actual values for your project.

The session.py file in the project reads these environment variables and makes them available for use in the project. If any of these variables are not set, the application will not run correctly.

Remember to replace the placeholders with the actual environment variables your project uses.



 
