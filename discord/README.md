## Purpose
This folder contains the terraform and python scripts to create a lambda function that has an api gateway (apigw) trigger, and uses the trigger to run the lambda_function.py script as a layer in the lambda.

## How to Deploy 
<!-- TODO clean this up -->
1. clone and git pull
2. python install dependencies to local folder
3. zip up lambda_function.py and dependencies
   - https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
4. zip file name must match value in aws_s3_object, I use 'deployment_package.zip'
5. terraform apply