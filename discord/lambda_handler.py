import boto3
import os
import nacl
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

def lambda_handler(event, context):
    # Insert some logic on checking message size and sanity
    botPubKey = os.environ['PUBLIC_KEY']
    verify_key = VerifyKey(bytes.fromhex(botPubKey))

    signature = event.headers["X-Signature-Ed25519"]
    timestamp = event.headers["X-Signature-Timestamp"]
    body = event.data

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
    except BadSignatureError:
        return {
                "statusCode": 401,
                "body": 'invalid request signature',
            }


    # Respond to /ping test
    if event['body'] == 'ping':
        # may need python json dumps here
        return { 
            "type": 4,  
            "data": { "content": "pong" }
        }

    # Respond to /getIP
    if event['body'] == 'getIP':
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
                return { 
                    "type": 4,  
                    "data": { "content": eni }
                }