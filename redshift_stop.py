"""Stop and delete a Redshift cluster.

    This script will:
    1. Shutdown the Redshift cluster.
    2. Delete the security group that opened up the Redshift port.
    3. Delete the IAM role setup for Redshift accessing S3.
"""

import argparse
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

# Shutdown the Redshift cluster
redshift = boto3.client("redshift")
redshift.delete_cluster(
    ClusterIdentifier=config.redshift_cluster_identifier,
    SkipFinalClusterSnapshot=True,
)

# Delete the security group that opened up the Redshift port
ec2 = boto3.resource("ec2")
security_group = list(
    ec2.security_groups.filter(GroupNames=[config.ec2_security_group_name])
)[0]
if security_group.ip_permissions:
    security_group.revoke_ingress(IpPermissions=security_group.ip_permissions)
if security_group.ip_permissions_egress:
    security_group.revoke_egress(
        IpPermissions=security_group.ip_permissions_egress
    )
security_group.delete()

# Delete the IAM role setup for Redshift accessing S3
iam = boto3.client("iam")
iam.detach_role_policy(
    RoleName=config.iam_role_name,
    PolicyArn="arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
)
iam.delete_role(RoleName=config.iam_role_name)
