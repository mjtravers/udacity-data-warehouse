"""Start a Redshift cluster.

    Assumes that you are connecting to AWS using an IAM user that
    has the AmazonRedshiftFullAccess policy attached.

    Log in credentials and default region must be set up in the
    ~/.aws/credentials and ~/.aws/config files respectively or as
    environment variables.

    This script will:
    1. Create an IAM role for Redshift to access S3.
    2. Discover the default VPC and open the Redshift port.
    3. Spin up the Redshift cluster.
    4. Wait for the cluster to become available.
    5. Print the connection string for the Redshift cluster.
"""

import argparse
import json
import boto3
from awsconfig import AwsConfig

parser = argparse.ArgumentParser()
parser.add_argument(
    "-c",
    "--config",
    type=str,
    help="path to the configuration file",
)
args = parser.parse_args()

config = AwsConfig(args.config)

# Set up a service role for Redshift to access S3 and retrieve the role ARN
iam = boto3.client("iam")
try:
    iam.create_role(
        RoleName=config.iam_role_name,
        Description="Service role for Redshift",
        AssumeRolePolicyDocument=json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "redshift.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        ),
    )
    iam.attach_role_policy(
        RoleName=config.iam_role_name,
        PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
    )
except iam.exceptions.EntityAlreadyExistsException:
    print(f"Role {config.iam_role_name} already exists, moving on")
role_arn = iam.get_role(RoleName=config.iam_role_name)["Role"]["Arn"]

# Discover the default VPC and open the Redshift port
ec2 = boto3.client("ec2")
response = ec2.describe_vpcs(
    Filters=[{"Name": "isDefault", "Values": ["true"]}]
)
default_vpc_id = response["Vpcs"][0]["VpcId"]
try:
    response = ec2.create_security_group(
        GroupName=config.ec2_security_group_name,
        Description="Security group to open up Redshift port",
        VpcId=default_vpc_id,
    )
    security_group_id = response["GroupId"]
    ec2.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": int(config.redshift_port),
                "ToPort": int(config.redshift_port),
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            }
        ],
    )
except ec2.exceptions.ClientError as e:
    if "InvalidGroup.Duplicate" in str(e):
        print(
            f"Security group {config.ec2_security_group_name} already exists"
        )
        # Get the security group id given a security group name
        response = ec2.describe_security_groups(
            Filters=[
                {
                    "Name": "group-name",
                    "Values": [config.ec2_security_group_name],
                }
            ]
        )
        security_group_id = response["SecurityGroups"][0]["GroupId"]

    else:
        raise e

# Spin up the Redshift cluster
redshift = boto3.client("redshift")
redshift.create_cluster(
    ClusterType=config.redshift_cluster_type,
    NodeType=config.redshift_node_type,
    NumberOfNodes=int(config.redshift_num_nodes),
    DBName=config.redshift_db_name,
    ClusterIdentifier=config.redshift_cluster_identifier,
    VpcSecurityGroupIds=[security_group_id],
    MasterUsername=config.redshift_db_user,
    MasterUserPassword=config.redshift_db_password,
    IamRoles=[role_arn],
)

# Wait for the cluster to become available
print("Waiting for the cluster to become available...")
waiter = redshift.get_waiter("cluster_available")
waiter.wait(ClusterIdentifier=config.redshift_cluster_identifier)

# Print the connection string for the Redshift cluster
print(config.db_connection)
