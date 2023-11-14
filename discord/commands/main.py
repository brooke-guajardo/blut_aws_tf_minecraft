import json
import boto3
import discord
from discord import app_commands
from discord.ext import commands

try:
    tokenfile = open('secret.json')
    secret = json.load(tokenfile)
except Exception as e:
    print("Unable to load token.")
    print(f"Exception: {e}")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = '!', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.tree.command(description="Ping Lambda to turn on MC server")
async def wakeup(interaction: discord.Interaction):
    await interaction.response.send_message()
    
@bot.tree.command(description="Grab Public IP of ECS Fargate")
async def getIP(interaction: discord.Interaction):
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
            embed = discord.Embed(f"Public IP Address: {eni}", title='Minecraft IP Address')
            await interaction.response.send_message(embed=embed)

def turnOffServer():
    client = boto3.client('ecs',region_name='us-east-1')
    off_response = client.update_service(
    cluster='minecraft_server',
    service='minecraft_server',
    desiredCount=0)

@bot.tree.command(description="Grab Public IP of ECS Fargate")
async def turnOnServer():
    client = boto3.client('ecs',region_name='us-east-1')
    off_response = client.update_service(
    cluster='minecraft_server',
    service='minecraft_server',
    desiredCount=1)

bot.run(secret['token'])