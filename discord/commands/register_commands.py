import os
import requests

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
        "name": "getIP",
        "type": 1,
        "description": "returns jardo's mc server IP address ... hopefully"
    },
    # Add more commands here in the same format
]

response = requests.post(url, json=commands_to_register, headers=headers)

if response.status_code == 201:
    print("Commands registered successfully!")
else:
    print(f"Failed to register commands. Status code: {response.status_code}")
    print(response.text)