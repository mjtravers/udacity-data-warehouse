# Udacity Data Engineering - Data Warehouse Project

## Purpose

The purpose of this project is to create an ETL process to create and populate analytical data warehouse tables for a fictional song distributing company, Sparkify. The raw data has been provided in AWS S3 buckets and contains song information and logs of user events when songs are requested and streamed.

## Design

The datawarehouse has been designed in a star-schema with the main fact table containing an individual song play event. The associated dimensional tables contain additional information about the song artist, user, song, and time the song was streamed.

The star-schema design is appropriate for performing analytics centered on user song preferences and associated characteristics such as user location, popularitiy of songs and artists, and whether the user was using the free or paid service from Sparkify.

## Discussion

As part of IaC (infrastructure as code), additional redshift_start.py and redshift_stop.py scripts were added to the project. A AWSConfig class was added to more easily manage configuration data across scripts.

Depending on the need of the analysts, rules on how to handle blank fields or incomplete records would be formulated and encoded into the ETL process.

The speed at which pulling song data from the S3 bucket was quite slow and burned up a lot of AWS credits. Testing was done on a subset of data to mitigate this problem.

## Project Files

- analysis_sql.py - Stand alone script to display a sample of analytical querires run against the data warehouse after it's populated.

- awsconfig.py - Class to more easily manage configuration parameters across scripts.

- create_tables.py - Script to drop and create database tables.

- data_warehouse.cfg - AWS configuration paremeters for the AWS services: IAM, EC2, Redshift, and S3. When setting up local environment to run project, it is assumed the AWS credentials are available either through ~/.aws/credentials or in the environment variables.

- etl.py - Script to load the staging tables and then pull records from the staging tables into the star-schema data warehouse tables.

- redshift_start.py - IaC script to configure and launch a Redshift cluster.

- redshift_stop.py - IaC script to stop a running Redshift cluster.

- sql_queries.py - Script containing the SQL queries used by the create_tables.py and etl.py scripts.
