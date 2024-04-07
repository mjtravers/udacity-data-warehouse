"""A sample of analytical queries to report on the data warehouse data."""

import psycopg2
from awsconfig import AwsConfig

config = AwsConfig()

# Establish a connection
conn = psycopg2.connect(config.db_connection)
cur = conn.cursor()

cur.execute(
    """
    SELECT COUNT(*) FROM staging_events;
"""
)
results = cur.fetchone()
print(f"Total number of events in staging: {results[0]}")

cur.execute(
    """
    SELECT COUNT(*) FROM staging_songs;
"""
)
results = cur.fetchone()
print(f"Total number of songs in staging: {results[0]}")

cur.execute(
    """
    SELECT a.name, s.title, COUNT(*) as plays
    FROM songplays p
    JOIN artists a ON p.artist_id  = a.artist_id
    JOIN songs s ON s.song_id = p.song_id
    GROUP BY (a.name, s.title)
    ORDER BY plays DESC;
"""
)
results = cur.fetchone()
print(
    f"Most played song with {results[2]} plays is {results[1]} by {results[0]}"
)

cur.execute(
    """
    SELECT location, COUNT(*) as plays
    FROM songplays
    GROUP BY (location)
    ORDER BY plays DESC;
"""
)
results = cur.fetchone()
print(f"Most active location with {results[1]} plays is {results[0]}")

cur.close()
conn.close()
