# Fargate Instructions

## Create ECR
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

cd ecr
terraform init
terraform apply
```

## Build image with non-auto download files copied over

Note: Below I have `v1.0.0` this value needs to match what you put in the ecs/ecs.tf file. And if you ever rebuild the image, you need to bump the version since the ECR was set to immutable. 
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export AWS_ACCOUNT_ID=your_aws_account_id
export AWS_REGION=your_aws_region

cd build
docker build . -t jardo_minecraft:v1.0.0
docker image ls # to confirm it was made properly, get the IMAGE_ID
aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com
docker tag IMAGE_ID "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/minecraft:v1.0.0
docker push "${AWS_ACCOUNT_ID}".dkr.ecr."${AWS_REGION}".amazonaws.com/minecraft:v1.0.0
```

## Terraform
```bash
# env vars set NOT RECOMMMENDED (:
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key

terraform init
terraform apply
```

# Client instructions
- Install CurseForge: https://www.curseforge.com/download/app
- Install ATM9 version `All the Mods 9-0.2.15` link [here](https://www.curseforge.com/minecraft/modpacks/all-the-mods-9/files?page=1&pageSize=20) with CurseForge.
- This should make a new entry under the 'My Modpacks' tab in your CurseForge app, click play on the top left :p
- This should bring up your MC launcher, use java edition
- The screen may look red and scary, don't be afraid Andi
- Once launcher has loaded click MULTIPLAYER
- Select direct connect and put IP without port (I'll provide from AWS console)
- done :tada:

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