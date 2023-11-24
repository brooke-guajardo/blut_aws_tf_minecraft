import os
import requests
import time

app_id = os.environ.get('DISCORD_APP_ID')
guild_id = os.environ.get('DISCORD_SERVER_ID')
bot_token = os.environ.get('DISCORD_BOT_TOKEN')

url = f"https://discord.com/api/v8/applications/{app_id}/guilds/{guild_id}/commands"

headers = {
    "Authorization": f"Bot {bot_token}",
    "Content-Type": "application/json"
}

commands_to_register = [
    {
        "name": "ping",
        "type": 1,
        "description": "replies with pong, simple slash health check"
    },
    {
        "name": "get_ip",
        "type": 1,
        "description": "returns jardo's mc server IP address ... hopefully"
    },
    {
        "name": "turn_off_mc",
        "type": 1,
        "description": "Turn off mc fargate server by scaling instances down to 0. This should also save before scaling down."
    },
    {
        "name": "turn_on_mc",
        "type": 1,
        "description": "Turn on mc fargate server by scaling instances up to 1."
    },
    {
        "name": "who_online",
        "type": 1,
        "description": "List users that are online connected to the server."
    },
    {
        "name": "save_mc",
        "type": 1,
        "description": "Run RCON /save-all to save the world."
    },
    {
        "name": "menu",
        "type": 1,
        "description": "List available commands in button format."
    }
]

# Register commands in bulk
for command in commands_to_register:
    command_url = url
    response = requests.post(command_url, json=command, headers=headers)

    if response.status_code == 201:
        print(f"Command '{command['name']}' registered successfully!")
    else:
        print(f"Failed to register command '{command['name']}'. Status code: {response.status_code}")
        print(response.text)  # To see the error message from Discord, if any
    time.sleep(1)

# Bulk overwrite if already registered and updating
response = requests.put(url, json=commands_to_register, headers=headers)
if response.status_code == 200:
    print(f"Bulk overwrite ran successfully, output:{response}")
else:
    print(f"Failed to bulk overwrite. Status code: {response.status_code}")
    print(response.text)