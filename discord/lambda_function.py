import boto3
import os
import nacl
import json
import requests
import mctools
from mctools import RCONClient
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

def lambda_handler(event, context):
    print(event)
    rconPass = os.environ['RCON_PASSWORD']
    botPubKey = os.environ['PUBLIC_KEY']
    disAppID = os.environ['DISCORD_APP_ID']
    verify_key = VerifyKey(bytes.fromhex(botPubKey))

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

        if body_json['data']['name'] == 'ping':
            print("[INFO] attempting to pong...")
            interaction_response(f"po-", body_json['id'],body_json['token'])
            interaction_reply(f"-ng", disAppID, body_json['token'])
            exit(0)

        if body_json['data']['name'] == 'get_ip':
            command_handler(
                disAppID,
                body_json,
                "get_ip",
                get_ip,
            )
            exit(0)

        if body_json['data']['name'] == 'turn_off_mc':
            function_list = [
                (rcon_list, (rconPass,)),
                (rcon_save, (rconPass,)),
                (scale_count, (0,))
            ]
            multi_command_handler(
                disAppID,
                body_json,
                "turn_off_mc",
                function_list
            )
            exit(0)

        if body_json['data']['name'] == 'turn_on_mc':
            command_handler(
                disAppID,
                body_json,
                "turn_on_mc",
                scale_count,
                1
            )
            exit(0)

        if body_json['data']['name'] == 'who_online':
            command_handler(
                disAppID,
                body_json,
                "who_online",
                rcon_list,
                rconPass
            )
            exit(0)

        if body_json['data']['name'] == 'save_mc':
            command_handler(
                disAppID,
                body_json,
                "who_online",
                rcon_save,
                rconPass
            )
            exit(0)
        
        if body_json['data']['name'] == 'menu':
            component_menu(f"Menu:", body_json['id'], body_json['token'])
            exit(0)

    # MESSAGE_COMPONENT
    if body_json['type'] == 3:
        component_respond(f"You clicked a button! IR", body_json['id'], body_json['token'])
        exit(0)


    # I would return 404 here but then the command will just error with no info
    # So pivoting to interaction reply so there is context in discord
    print(f"[ERROR] Command made it to end without properly being handled. Either the command is invalid or the above did not exit properly.")
    interaction_reply(f"[ERROR] End of Lambda", disAppID, body_json['token'])

def command_handler(disAppID, body_json, command_name, command_func, *args, **kwargs):
    try:
        interaction_response(f"ACK for {command_name} command", body_json['id'], body_json['token'])
        response = command_func(*args, **kwargs)
        print(f"Return from {command_func}: {response}") # Debug Output
        # Don't want boto3 output, it contains account info
        if command_func != scale_count:
            interaction_reply(response, disAppID, body_json['token'])
        else:
            interaction_reply(f"Scaling completed.", disAppID, body_json['token'])
    except Exception as e:
        print(f"[ERROR] {command_name}: {e}")
        interaction_reply(f"[ERROR] {command_name}", disAppID, body_json['token'])

def multi_command_handler(disAppID, body_json, command_name, function_list, *args, **kwargs):
    try:
        interaction_response(f"ACK for {command_name} command", body_json['id'], body_json['token'])
        for func, func_args in function_list:
            response = func(*func_args, **kwargs)
            print(f"Function: {func} \nResponse: {response}") # Debug Output
            # Don't want boto3 output, it contains account info
            if func != scale_count:
                interaction_reply(response, disAppID, body_json['token'])
            else:
                interaction_reply(f"Scaling completed.", disAppID, body_json['token'])
    except Exception as e:
        print(f"[ERROR] {command_name}: {e}")
        interaction_reply(f"[ERROR] {command_name}", disAppID, body_json['token'])

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

def interaction_reply(data, application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"
    print(url)
    json = {
        "content": data
    }  
    r = requests.post(url, json=json)

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
                            "custom_id": "mc_save"
                        },
                        {
                            "type": 2,
                            "label": "Check who is online",
                            "style": 1,
                            "custom_id": "rcon_list"
                        }
                    ]
                }
            ],
            "flags": 64
        }
    }
    r = requests.post(url, json=json)
    print(f"Component Menu return: {r}")

def interaction_update(data, application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}/messages/@original"
    json = {
        "type": 4,
        "data": {
            "content": data
        }
    }  
    r = requests.patch(url, json=json)
    print(f"Interaction Update return: {r}")

def component_respond(data, interaction_id, interaction_token):
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 4,
        "data": {
            "content": data
        }
    }
    r = requests.post(url, json=json)
    print(f"Component Respond return: {r}")