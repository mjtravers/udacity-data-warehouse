"""Create tables for the data warehouse."""

import psycopg2
from awsconfig import AwsConfig
from sql_queries import create_table_queries, drop_table_queries

config = AwsConfig()


def drop_tables(cur, conn):
    """Drop database tables for a clean start."""
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """Create database tables defined in sql_queries.py."""
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    conn = psycopg2.connect(config.db_connection)
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
