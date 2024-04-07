"""Load data into Redshift data warehouse."""

import psycopg2
from awsconfig import AwsConfig
from sql_queries import copy_table_queries, insert_table_queries

config = AwsConfig()


def load_staging_tables(cur, conn):
    """Load staging tables from S3."""
    for query in copy_table_queries:
        cur.execute(query["template"], query["values"])
        conn.commit()


def insert_tables(cur, conn):
    """Insert star-schema tables from staging tables."""
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    conn = psycopg2.connect(config.db_connection)
    cur = conn.cursor()

    # load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
