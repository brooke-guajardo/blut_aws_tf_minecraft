import boto3
import os
import nacl
import json
import requests
import mctools
from mctools import RCONClient
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
rconPass = os.environ['RCON_PASSWORD']
botPubKey = os.environ['PUBLIC_KEY']
disAppID = os.environ['DISCORD_APP_ID']
verify_key = VerifyKey(bytes.fromhex(botPubKey))


def lambda_handler(event, context):
    print(event)
    signature = event['headers']['x-signature-ed25519']
    timestamp = event['headers']['x-signature-timestamp']
    body = event['body']

    try:
        body_json = json.loads(body)
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except (ValueError, KeyError, BadSignatureError) as e:
        return {
            "statusCode": 401,
            "body": 'Invalid request signature',
        }

    # Respond to Discord config ping
    # i.e. the 'INTERACTIONS ENDPOINT URL' test
    if body_json['type'] == 1:
        print(f"INTERACTIONS ENDPOINT URL test received.")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "type": 1
            })
        }

    # APPLICATION_COMMAND
    if body_json['type'] == 2:
        command_name = body_json['data']['name']
        handler = COMMAND_HANDLERS.get(command_name)
        if handler:
            handler(body_json)
            return

    # MESSAGE_COMPONENT
    if body_json['type'] == 3:
        component_id = body_json['data']['custom_id']
        handler = COMPONENT_HANDLERS.get(component_id)
        if handler:
            handler(body_json)
            return

            

    # I would return 404 here but then the command will just error with no info
    # So pivoting to interaction reply so there is context in discord
    print(f"[ERROR] Command made it to end without properly being handled. Either the command is invalid or the above did not exit properly.")
    interaction_reply(f"[ERROR] End of Lambda", body_json['token'])

def command_handler(body_json, command_name, command_func, *args, **kwargs):
    try:
        interaction_response(f"ACK for {command_name} command", body_json['id'], body_json['token'])
        response = command_func(*args, **kwargs)
        print(f"Return from {command_func}: {response}") # Debug Output
        # Don't want boto3 output, it contains account info
        if command_func != scale_count:
            interaction_reply(response, body_json['token'])
        else:
            interaction_reply(f"Scaling completed.", body_json['token'])
    except Exception as e:
        print(f"[ERROR] {command_name}: {e}")
        interaction_reply(f"[ERROR] {command_name}", body_json['token'])

def multi_command_handler(body_json, command_name, function_list, *args, **kwargs):
    try:
        interaction_response(f"ACK for {command_name} command", body_json['id'], body_json['token'])
        for func, func_args in function_list:
            response = func(*func_args, **kwargs)
            print(f"Function: {func} \nResponse: {response}") # Debug Output
            # Don't want boto3 output, it contains account info
            if func != scale_count:
                interaction_reply(response, body_json['token'])
            else:
                interaction_reply(f"Scaling completed.", body_json['token'])
    except Exception as e:
        print(f"[ERROR] {command_name}: {e}")
        interaction_reply(f"[ERROR] {command_name}", body_json['token'])

def get_ip():
    client = boto3.client('ecs',region_name='us-east-1')

    task_response = client.list_tasks(
        cluster='minecraft_server',
        serviceName='minecraft_server',
        desiredStatus='RUNNING',
        launchType='FARGATE'
    )

    task = task_response['taskArns'][0]

    detail_response = client.describe_tasks(
        cluster='minecraft_server',
        tasks=[
            task,
        ]
    )

    for detail in detail_response['tasks'][0]['attachments'][0]['details']:
        if detail['name'] == 'networkInterfaceId':
            eni_resource = boto3.resource("ec2",region_name='us-east-1').NetworkInterface(detail['value'])
            eni = eni_resource.association_attribute.get("PublicIp")
            return eni
    
    raise Exception("Boto3 failed to pull IP. Bad boto3!")

def scale_count(count: int):
    client = boto3.client('ecs',region_name='us-east-1')
    off_response = client.update_service(
    cluster='minecraft_server',
    service='minecraft_server',
    desiredCount=count)
    return off_response

def rcon_save(rpass):
    rcon = RCONClient(get_ip())
    success = rcon.login(rpass)

    # If rcon failed to auth, it supports retries but meh
    if success == False:
        print(f"RCON Failed to login")
        raise Exception("RCON Failed to login")

    rcon.command("/say ------------------------------------------")
    rcon.command("/say - Server is saving, it may also be shutting down. -")
    rcon.command("/say ------------------------------------------")

    rcon_response = rcon.command("/save-all")
    rcon.stop()
    return rcon_response[:-4]

def rcon_list(rpass):
    rcon = RCONClient(get_ip())
    success = rcon.login(rpass)

    # If rcon failed to auth, it supports retries but meh
    if success == False:
        print(f"RCON Failed to login")
        raise Exception("RCON Failed to login")
    
    rcon_response = rcon.command("/list")
    rcon.stop()
    return rcon_response[:-4]
        
def interaction_response(data, interaction_id, interaction_token):
    # Create Interaction Response
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 4,
        "data": {
            "content": data
        }
    }
    r = requests.post(url, json=json)
    print(f"Interaction Response return: {r}")

def interaction_reply(data, interaction_token):
    # Create Followup Message
    url = f"https://discord.com/api/v10/webhooks/{disAppID}/{interaction_token}"
    json = {
        "content": data
    }  
    r = requests.post(url, json=json)
    print(f"Interaction Reply return: {r}")

def component_menu(data, interaction_id, interaction_token):
    # Create Interaction Response
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 4,
        "data": {
            "content": data,
            "components": [
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Save Server Data",
                            "style": 1,
                            "custom_id": "mc_save_bt"
                        },
                        {
                            "type": 2,
                            "label": "Check Who is Online",
                            "style": 1,
                            "custom_id": "rcon_list_bt"
                        },
                        {
                            "type": 2,
                            "label": "Get Server IP",
                            "style": 1,
                            "custom_id": "get_ip_bt"
                        }
                    ]
                },
                {
                    "type": 1,
                    "components": [
                        {
                            "type": 2,
                            "label": "Turn on MC Server",
                            "style": 3,
                            "custom_id": "mc_on_bt"
                        },
                        {
                            "type": 2,
                            "label": "Turn off MC Server",
                            "style": 4,
                            "custom_id": "mc_off_bt"
                        }
                    ]
                }
            ],
            "flags": 64
        }
    }
    r = requests.post(url, json=json)
    print(f"Component Menu return: {r}")

def component_respond(data, interaction_id, interaction_token):
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 7,
        "data": {
            "content": data
        }
    }
    r = requests.post(url, json=json)
    print(f"Component Respond return: {r}")


# Individual command handlers used by lambda_handler
def handle_ping(body_json):
    print("[INFO] attempting to pong...")
    interaction_response("po-", body_json['id'], body_json['token'])
    interaction_reply("-ng", body_json['token'])


def handle_get_ip(body_json):
    command_handler(body_json, "get_ip", get_ip)


def handle_turn_off_mc(body_json):
    function_list = [
        (rcon_list, (rconPass,)),
        (rcon_save, (rconPass,)),
        (scale_count, (0,))
    ]
    multi_command_handler(body_json, "turn_off_mc", function_list)


def handle_turn_on_mc(body_json):
    command_handler(body_json, "turn_on_mc", scale_count, 1)


def handle_who_online(body_json):
    command_handler(body_json, "who_online", rcon_list, rconPass)


def handle_save_mc(body_json):
    command_handler(body_json, "who_online", rcon_save, rconPass)


def handle_menu(body_json):
    component_menu("Menu:", body_json['id'], body_json['token'])


# Mappings for quick lookup
COMMAND_HANDLERS = {
    "ping": handle_ping,
    "get_ip": handle_get_ip,
    "turn_off_mc": handle_turn_off_mc,
    "turn_on_mc": handle_turn_on_mc,
    "who_online": handle_who_online,
    "save_mc": handle_save_mc,
    "menu": handle_menu,
}


COMPONENT_HANDLERS = {
    "mc_save_bt": handle_save_mc,
    "rcon_list_bt": handle_who_online,
    "get_ip_bt": handle_get_ip,
    "mc_on_bt": handle_turn_on_mc,
    "mc_off_bt": handle_turn_off_mc,
}
