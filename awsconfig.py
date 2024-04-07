"""Manage configuration settings for the project."""

import configparser
import boto3

AWSCONFIG_DEFAULT_CONFIG_PATH = "data_warehouse.cfg"


class AwsConfig:
    """Utility class to provide configuration settings for the project."""

    def __init__(self, config_path=None):
        config = configparser.ConfigParser()
        if config_path:
            config.read(config_path)
        else:
            config.read(AWSCONFIG_DEFAULT_CONFIG_PATH)

        self.iam_role_name = config.get("IAM", "ROLE_NAME")
        self.ec2_security_group_name = config.get("EC2", "SECURITY_GROUP_NAME")
        self.redshift_cluster_type = config.get("REDSHIFT", "CLUSTER_TYPE")
        self.redshift_num_nodes = config.get("REDSHIFT", "NUM_NODES")
        self.redshift_node_type = config.get("REDSHIFT", "NODE_TYPE")
        self.redshift_cluster_identifier = config.get(
            "REDSHIFT", "CLUSTER_IDENTIFIER"
        )
        self.redshift_db_name = config.get("REDSHIFT", "DB_NAME")
        self.redshift_db_user = config.get("REDSHIFT", "DB_USER")
        self.redshift_db_password = config.get("REDSHIFT", "DB_PASSWORD")
        self.redshift_port = config.get("REDSHIFT", "PORT")
        self.s3_log_data = config.get("S3", "LOG_DATA")
        self.s3_song_data = config.get("S3", "SONG_DATA")
        self.s3_log_jsonpath = config.get("S3", "LOG_JSONPATH")

    @property
    def role_arn(self):
        """Retrieve the ARN for the IAM role."""
        iam = boto3.client("iam")
        return iam.get_role(RoleName=self.iam_role_name)["Role"]["Arn"]

    @property
    def db_connection(self):
        """Retrieve the database connection string."""
        redshift = boto3.client("redshift")
        response = redshift.describe_clusters(
            ClusterIdentifier=self.redshift_cluster_identifier
        )
        cluster_endpoint = response["Clusters"][0]["Endpoint"]["Address"]

        return (
            f"postgresql://{self.redshift_db_user}:"
            f"{self.redshift_db_password}@{cluster_endpoint}:"
            f"{self.redshift_port}/{self.redshift_db_name}"
        )
