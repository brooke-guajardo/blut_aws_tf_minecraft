# Welcome to my Repo
This is just a way for my friends and I can enjoy some MC that's hopefully a bit more cost effective than hosting services. As well as give more control! As the about says, this is an ECS Fargate Minecraft server that uses a Discord bot that runs on a Lambda with an API Gateway Trigger for slash command management. 

Happy to answer any questions, I'd like to make this more generic for others to use. For now it does have configs that are more tuned to what my friends and I are playing.

# Setup Instructions

## 1. Create AWS ECR
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

git clone https://github.com/brooke-guajardo/blut_aws_tf_minecraft.git
cd blut_aws_tf_minecraft/ecr
terraform init
terraform apply
```

## 2. Build Docker Image and Push to ECR
 Since we are leveraging the auto download handled by Curse Forge's API, we have to handle mods that owners have not enabled auto downloads. This requires you to locally download the mods, so that when building the docker file, the mods' jar files are copied over. More details [here](https://docker-minecraft-server.readthedocs.io/en/latest/mods-and-plugins/curseforge-files/).

I found what files I needed to manually download by locally running the docker image, more detailed steps [here](./docs/manual_downloads.md).

### Note: 
Below I have `v1.0.0` this value needs to match what you put in the ecs/ecs.tf file. And if you ever rebuild the image, you need to bump the version since the ECR is set to immutable. 
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export AWS_ACCOUNT_ID=your_aws_account_id
export AWS_REGION=your_aws_region
export TF_VAR_public_key=your_public_key

cd build
# before the docker build download and put into the build folder your jar files!
docker build . -t jardo_minecraft:v1.0.0
docker image ls # to confirm it was made properly, get the IMAGE_ID
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com
docker tag IMAGE_ID "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/minecraft:v1.0.0
docker push "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/minecraft:v1.0.0
```

## 3. Deploy ECS, EFS, VPC and Security Groups
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export TF_VAR_cf_api_key=your_curse_forge_api_key
export TF_VAR_rcon_pass=your_rcon_password


cd ecs
terraform init
terraform apply
```

## 4. Deploy Lambda, API Gateway, and supporting Infrastructure (Discord Bot)
This section assumes you have created your discord bot already, that you have a discord server that you own or can have your bot run in (you need the server's ID i.e. guild ID for registering your commands, though you can also make the commands global, further reading [here](https://discord.com/developers/docs/interactions/application-commands#create-global-application-command)), and you have RCON enabled in the ECS section of the terraform code.
  - Further reading for setting up a discord bot 
    - https://discord.com/developers/docs/getting-started
    - https://discord.com/developers/applications 

Also for the lambda function, it needs all libraries packaged with it as per AWS documentation. Below was my method of doing so
  - Further reading https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export TF_VAR_rcon_pass=your_rcon_password
export TF_VAR_public_key=your_public_key
export TF_VAR_discord_app_id=your_discord_bot_app_id
export DISCORD_SERVER_ID=your_discord_server_id
export DISCORD_BOT_TOKEN=your_discord_bot_token

cd discord
cd commands
# the output should tell you if they succeed
# also they'll show up in the server you are testing in if it works
python3 register_commands.py
cd .. # or back into the discord directory
# create python virtual environment
python3 -m venv venv
source venv/bin/activate
pip3 install pipreqs
# this will make the requirements.txt file
pipreqs .
pip3 install -r requirements.txt
cd venv/lib/python3.9/site-packages/
zip -r ../../../../deployment_package.zip .
# change directory back to discord/
cd -
# add the lamba function to the zip
zip deployment_package.zip lambda_function.py
terraform init
terraform apply
```

The output from this terraform will give you the APIGW url that you need to put into the settings of your discord bot.
  - https://discord.com/developers/applications
  - Click on your bot, and it should be the 'INTERACTIONS ENDPOINT URL'
  - Add your URL and save, if it errors, good luck o7, hopefully it works.
    - If any errors do occur, be sure to check your cloudwatch logs in the AWS console

# Client instructions
- Install CurseForge: https://www.curseforge.com/download/app
- Install ATM9 version `All the Mods 9-0.2.15` link [here](https://www.curseforge.com/minecraft/modpacks/all-the-mods-9/files?page=1&pageSize=20) with CurseForge.
- This should make a new entry under the 'My Modpacks' tab in your CurseForge app
- Export this profile checking everything except saves and expand the mod folder section and unselect `allthewizardgear`
- This should make a zip file
- On the top left of curseforge, select 'Create Custom Profile'
- Select the 'import a previously creaed profile' option on the pop up
- Use the zip file you just made
- This should make another entry under the 'My Modpacks' tab in your CurseForge app, I suggest you edit and rename it. And delete the first ATM9 profile
- Select play on this new modpack profile
- This should bring up your MC launcher, use java edition
- The screen may look red and scary, don't be afraid Andi
- Once launcher has loaded click MULTIPLAYER
- Select direct connect and put IP without port (I'll provide from AWS console)
- done :tada:

## Discord Bot Usage
Full Command List
- `/save_mc` to ad hoc save the server
- `/who_online` to see who is online, may error if server is off
- `/get_ip`
- `/turn_on_mc`
- `/turn_off_mc` will RCON save and then shut off server, also puts message in all chat
- `/menu` to bring up the above commands in a UI menu with buttons
![image](https://github.com/brooke-guajardo/blut_aws_tf_minecraft/assets/102095955/50e0a581-87bb-4899-9ea3-4008f40deac1)


To get the service IP address please use `/get_ip` don't worry if it fails, the lambda is finicky, just wait a moment and run the command again. 
If get_ip returns "list index out of range" it means the server is not up, no worries! Turn on the minecraft server with `/turn_on_mc` wait a minute or two (at most like 5 mins?) and you should be able to get the IP
When done, you should be able to run `/turn_off_mc` from discord this command will now run RCON /save-all against the server before scaling down the instances to 0.

## References
- https://hub.docker.com/r/itzg/minecraft-server/tags
- https://docker-minecraft-server.readthedocs.io/en/latest/types-and-platforms/mod-platforms/auto-curseforge/#api-key
- https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
- https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html 
- https://banhawy.medium.com/3-ways-to-configure-terraform-to-use-your-aws-account-fb00a08ded5
- https://github.com/tfutils/tfenv
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/getting-started-cli.html
- https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html
- https://medium.com/@ilia.lazebnik/attaching-an-efs-file-system-to-an-ecs-task-7bd15b76a6ef
- https://stackoverflow.com/questions/65134711/error-incorrect-attribute-value-type-module-network-private-subnets0-is-tuple
- https://docs.aws.amazon.com/efs/latest/ug/accessing-fs-create-security-groups.html
- https://shisho.dev/dojo/providers/aws/Amazon_EFS/aws-efs-access-point/
- https://github.com/pgreene/terraform-aws-efs-access-point/blob/main/efs-access-point.tf
- https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecs_task_definition#example-using-efs_volume_configuration
- https://github.com/Yris-ops/minecraft-server-aws-ecs-fargate/blob/main/main.tf
- https://developer.hashicorp.com/terraform/tutorials/aws/lambda-api-gateway#clone-example-configuration
- https://github.com/oozio/discord_aws_bot_demo/tree/master

## Pre-generated worlds (TODO)
1. Reference branch `init_pregen` you will need a folder in the build directory and some changes to the docker file. 
2. Then 2 env vars that you only want to run once against your ECS or else you'll lose progress that's been written to your EFS.
3. Once you have those changes
4. Build new image and upload to ECR
5. Deploy to ECS the new env var and with the new docker image tag
