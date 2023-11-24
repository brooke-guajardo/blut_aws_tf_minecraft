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

    # Respond to Discord config ping, i.e. the 'INTERACTIONS ENDPOINT URL' test
    if body_json['type'] == 1:
        print(f"INTERACTIONS ENDPOINT URL test received.")
        return {
            "statusCode": 200,
            "body": json.dumps({
                "type": 1
            })
        }


    # Bot Access and Channel Ping Pong Test
    if body_json['data']['name'] == 'ping':
        print("[INFO] attempting to pong...")
        interaction_response(f"po-", body_json['id'],body_json['token'])
        interaction_reply(f"-ng", disAppID, body_json['token'])
        return generate_response("pong.")

    # Bot get_ip slash command
    if body_json['data']['name'] == 'get_ip':
        command_handler(
            disAppID,
            rconPass,
            body_json,
            "get_ip",
            get_ip,
        )

    if body_json['data']['name'] == 'turn_off_mc':
        try:
            interaction_response(f"ACK turning off MC server", body_json['id'],body_json['token'])
            rcon_response = rcon_save(rconPass)
            print(f"{rcon_response}")
            interaction_reply(f"RCON saving server.\n{rcon_response}", disAppID, body_json['token'])
            boto_response = scale_count(0)
            print(f"{boto_response}")
            interaction_reply(f"Boto3 scaled down server", disAppID, body_json['token'])
            return generate_response(f"end of turning off MC server")
        except Exception as e:
            print(f"[ERROR] turn_off_mc: {e}")
            interaction_reply(f"[ERROR] turn_off_mc", disAppID, body_json['token'])
        finally:
            return generate_response(f"[ERROR] turn_off_mc")

    if body_json['data']['name'] == 'turn_on_mc':
        command_handler(
            disAppID,
            rconPass,
            body_json,
            "turn_on_mc",
            scale_count,
            1
        )

    if body_json['data']['name'] == 'who_online':
        command_handler(
            disAppID,
            rconPass,
            body_json,
            "who_online",
            rcon_list,
            rconPass
        )

    if body_json['data']['name'] == 'save_mc':
        command_handler(
            disAppID,
            rconPass,
            body_json,
            "who_online",
            rcon_save,
            rconPass
        )

    # I would return 404 here but then the command will just error with no info
    # So pivoting to interaction reply so there is context in discord
    print(f"[ERROR] Command made it to end without properly being handled. Either the command is invalid or the above did not exit properly.")
    interaction_reply(f"[ERROR] End of Lambda", disAppID, body_json['token'])

def command_handler(disAppID, rconPass, body_json, command_name, command_func, *args, **kwargs):
    try:
        interaction_response(f"ACK for {command_name} command", body_json['id'], body_json['token'])
        response = command_func(*args, **kwargs)
        # Debug Output
        print(repsonse)
        # Don't want boto3 output, it contains account info
        if command_func != 'scale_count':
            interaction_reply(response, disAppID, body_json['token'])
        else:
            interaction_reply(f"Scaling completed.", disAppID, body_json['token'])
        return generate_response(f"End of {command_name} command")
    except Exception as e:
        print(f"[ERROR] {command_name}: {e}")
        interaction_reply(f"[ERROR] {command_name}", disAppID, body_json['token'])
    finally:
        return generate_response(f"[ERROR] {command_name}")   

def generate_response(data, status_code=200):
    print(data)
    response_payload = {
    "type": 4,
    "data": {
        "tts": False,
        "content": data,
        "embeds": [],
        "allowed_mentions": {"parse": []}
        }
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(response_payload)
    }

    return response

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
    url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
    json = {
        "type": 4,
        "data": {
            "content": data
        }
    }
    r = requests.post(url, json=json)

def interaction_reply(data, application_id, interaction_token):
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}"
    json = {
        "content": data
    }  
    r = requests.post(url, json=json)