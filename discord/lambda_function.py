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
    if body_json['type'] == 1:
        print(f"GOOD")
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
        print("[INFO] Starting to Fetch IP ...")
        try:
            interaction_response(f"ACK fetching IP", body_json['id'],body_json['token'])
            mc_ip = get_ip()
            interaction_reply(f"Server IP is: {mc_ip}", disAppID, body_json['token'])
            return generate_response(f"end of get ip")
        except Exception as e:
            print(f"[ERROR] get_ip: {e}")
            return generate_response(f"[ERROR] get_ip: @jardorook look at them logs!")

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
            return generate_response(f"[ERROR] turn_off_mc: @jardorook look at them logs!")

    if body_json['data']['name'] == 'turn_on_mc':
        try:
            interaction_response(f"ACK turning on MC server", body_json['id'],body_json['token'])
            boto_response = scale_count(1)
            print(f"{boto_response}")
            interaction_reply(f"Boto3 scaled instance count to 1. I.e. MC server is starting up.", disAppID, body_json['token'])
            return generate_response(f"end of turning on MC server")
        except Exception as e:
            print(f"[ERROR] turn_on_mc: {e}")
            return generate_response(f"[ERROR] turn_on_mc: @jardorook look at them logs!")

    if body_json['data']['name'] == 'who_online':
        try:
            interaction_response(f"ACK checking who is online connected to MC server", body_json['id'],body_json['token'])
            rcon_response = rcon_list(rconPass)
            print(f"{rcon_response}")
            interaction_reply(f"{rcon_response}", disAppID, body_json['token'])
            return generate_response(f"end of checking who is online")
        except Exception as e:
            print(f"[ERROR] who_online: {e}")
            return generate_response(f"[ERROR] who_online: @jardorook look at them logs!")   

    if body_json['data']['name'] == 'save_mc':
        try:
            interaction_response(f"ACK running RCON /save-all", body_json['id'],body_json['token'])
            rcon_response = rcon_save(rconPass)
            interaction_reply(f"{rcon_response}", disAppID, body_json['token'])
            return generate_response(f"end of saving server")
        except Exception as e:
            print(f"[ERROR] save_mc: {e}")
            return generate_response(f"[ERROR] save_mc: @jardorook look at them logs!")   

    # 404 if gets to here, handlers failed or command was not valid
    print(f"never caught")
    return generate_response(f"Something went wrong dawg. Jardo go fix you crap!")

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
    print("meow")
    rcon = RCONClient(get_ip())
    success = rcon.login(rpass)

    # If rcon failed to auth, it supports retries but meh
    if success == False:
        print(f"RCON Failed to login")
        raise Exception("RCON Failed to login")
    print("bork")
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