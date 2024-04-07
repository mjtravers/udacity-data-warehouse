"""SQL queries for pipeline ETL process."""

from awsconfig import AwsConfig


# CONFIG
config = AwsConfig()

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplays_table_drop = "DROP TABLE IF EXISTS songplays;"
users_table_drop = "DROP TABLE IF EXISTS users;"
songs_table_drop = "DROP TABLE IF EXISTS songs;"
artists_table_drop = "DROP TABLE IF EXISTS artists;"
times_table_drop = "DROP TABLE IF EXISTS times;"

# CREATE TABLES

staging_events_table_create = """
    CREATE TABLE staging_events (
        artist                varchar(250)  null,
        auth                  varchar(10)   null,
        firstName             varchar(50)   null,
        gender                char(1)       null,
        itemInSession         integer       null,
        lastName              varchar(50)   null,
        length                numeric(9,5)  null,
        level                 varchar(10)   null,
        location              varchar(50)   null,
        method                varchar(10)   null,
        page                  varchar(20)   null,
        registration          numeric(13,0) null,
        sessionId             integer       null,
        song                  varchar(250)  null,
        status                integer       null,
        ts                    timestamp     null,
        userAgent             varchar(150)  null,
        userId                integer       null
    );

"""

staging_songs_table_create = """
    CREATE TABLE staging_songs (
        num_songs             integer       null,
        artist_id             varchar(18)   null,
        artist_latitude       numeric(9,6)  null,
        artist_longitude      numeric(9,6)  null,
        artist_location       varchar(400)  null,
        artist_name           varchar(400)  null,
        song_id               varchar(18)   null,
        title                 varchar(400)  null,
        duration              numeric(9,5)  null,
        year                  integer       null
    );
"""

songplays_table_create = """
    CREATE TABLE songplays (
        songplay_id           integer       identity(0,1) primary key,
        start_time            timestamp     null,
        user_id               integer       null,
        level                 varchar(10)   null,
        song_id               varchar(18)   null,
        artist_id             varchar(18)   null,
        session_id            integer       null,
        location              varchar(50)   null,
        user_agent            varchar(150)  null
    );
"""

users_table_create = """
    CREATE TABLE users (
        user_id               integer       primary key,
        first_name            varchar(50)   null,
        last_name             varchar(50)   null,
        gender                char(1)       null,
        level                 varchar(10)   null
    );
"""

songs_table_create = """
    CREATE TABLE songs (
        song_id               varchar(18)   primary key,
        title                 varchar(400)  null,
        artist_id             varchar(18)   null,
        year                  integer       null,
        duration              numeric(9,5)  null
    );
"""

artists_table_create = """
    CREATE TABLE artists (
        artist_id             varchar(18)   primary key,
        name                  varchar(400)  null,
        location              varchar(400)  null,
        latitude              numeric(9,6)  ,
        longitude             numeric(9,6)
    );
"""

times_table_create = """
    CREATE TABLE times (
        start_time            timestamp     primary key,
        hour                  integer       null,
        day                   integer       null,
        week                  integer       null,
        month                 integer       null,
        year                  integer       null,
        weekday               integer       null
    );
"""

# STAGING TABLES
staging_events_copy = {
    "template": """
        COPY staging_events FROM %s
        IAM_ROLE %s
        JSON %s
        TIMEFORMAT 'epochmillisecs'
        REGION 'us-west-2';
    """,
    "values": (config.s3_log_data, config.role_arn, config.s3_log_jsonpath),
}

staging_songs_copy = {
    "template": """
        COPY staging_songs FROM %s
        IAM_ROLE %s
        JSON 'auto'
        REGION 'us-west-2';
    """,
    "values": (config.s3_song_data, config.role_arn),
}

# FINAL TABLES

songplays_table_insert = """
    INSERT INTO songplays (
        start_time,
        user_id,
        level,
        song_id,
        artist_id,
        session_id,
        location,
        user_agent
    ) SELECT DISTINCT
        e.ts,
        e.userId,
        e.level,
        s.song_id,
        s.artist_id,
        e.sessionId,
        e.location,
        e.userAgent FROM staging_events e
        JOIN staging_songs s
        ON e.song = s.title
        AND e.artist = s.artist_name
"""

users_table_insert = """
    INSERT INTO users (
        user_id,
        first_name,
        last_name,
        gender,
        level
    ) SELECT DISTINCT
        userId,
        firstName,
        lastName,
        gender,
        level
        FROM staging_events
        WHERE userId is not null
"""

songs_table_insert = """
    INSERT INTO songs (
        song_id,
        title,
        artist_id,
        year,
        duration
    ) SELECT DISTINCT
        song_id,
        title,
        artist_id,
        year,
        duration
        FROM staging_songs
"""

artists_table_insert = """
    INSERT INTO artists (
        artist_id,
        name,
        location,
        latitude,
        longitude
    ) SELECT DISTINCT
        artist_id,
        artist_name,
        artist_location,
        artist_latitude,
        artist_longitude
        FROM staging_songs
"""

times_table_insert = """
    INSERT INTO times (
        start_time,
        hour,
        day,
        week,
        month,
        year,
        weekday
    ) SELECT DISTINCT
        ts,
        EXTRACT(hour FROM ts),
        EXTRACT(day FROM ts),
        EXTRACT(week FROM ts),
        EXTRACT(month FROM ts),
        EXTRACT(year FROM ts),
        EXTRACT(weekday FROM ts)
        FROM staging_events
"""

# QUERY LISTS

create_table_queries = [
    staging_events_table_create,
    staging_songs_table_create,
    songplays_table_create,
    users_table_create,
    songs_table_create,
    artists_table_create,
    times_table_create,
]
drop_table_queries = [
    staging_events_table_drop,
    staging_songs_table_drop,
    songplays_table_drop,
    users_table_drop,
    songs_table_drop,
    artists_table_drop,
    times_table_drop,
]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [
    songplays_table_insert,
    users_table_insert,
    songs_table_insert,
    artists_table_insert,
    times_table_insert,
]
