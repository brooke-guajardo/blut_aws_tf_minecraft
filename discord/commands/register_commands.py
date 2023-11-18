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
        "name": "get_ip",
        "type": 1,
        "description": "returns jardo's mc server IP address ... hopefully"
    },
    {
        "name": "turn_off_mc",
        "type": 1,
        "description": "Turn off mc fargate server by scaling instances down to 0."
    },
    {
        "name": "turn_on_mc",
        "type": 1,
        "description": "Turn on mc fargate server by scaling instances up to 1."
    }
]

# Delete commands in bulk to reset if needed
for command in commands_to_register:
    command_url = url
    response = requests.delete(command_url, json=command, headers=headers)

    if response.status_code == 204:
        print(f"Command '{command['name']}' deleted successfully!")
    else:
        print(f"Failed to delete command '{command['name']}'. Status code: {response.status_code}")
        print(response.text)  # To see the error message from Discord, if any


# Register commands in bulk
for command in commands_to_register:
    command_url = url
    response = requests.post(command_url, json=command, headers=headers)

    if response.status_code == 201:
        print(f"Command '{command['name']}' registered successfully!")
    else:
        print(f"Failed to register command '{command['name']}'. Status code: {response.status_code}")
        print(response.text)  # To see the error message from Discord, if any