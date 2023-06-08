import subprocess

from pygit2 import Repository

from pathlib import Path

import boto3
from botocore.client import ClientError

allowed_branches = ["master"]

aws_default_region = "sa-east-1"

ssm_client = boto3.client('ssm', region_name = aws_default_region)


sts_client = boto3.client('sts', region_name = aws_default_region)
s3_client = boto3.resource('s3', region_name = aws_default_region)

def main():
    repository = Repository('.')
    git_branch = repository.head.shorthand
    
    repository_name = Path(repository.remotes['origin'].url).stem

    if(not git_branch in allowed_branches):
        raise
    
    project_name = ssm_client.get_parameter(Name = "ProjectName")['Parameter']['Value']

    if(not project_name in repository_name):
        raise

    deploy_bucket = ssm_client.get_parameter(Name = "DeployBucket")['Parameter']['Value']

    result = subprocess.call(['sam.cmd', 'deploy', '--template-file', './resources.yml', '--capabilities', 'CAPABILITY_IAM', '--s3-bucket', deploy_bucket, '--s3-prefix', 'project-builder/stack-network', '--region', aws_default_region, '--stack-name', 'stack-network', '--no-fail-on-empty-changeset'])

    print(result)

    


if __name__ == "__main__":
    main()