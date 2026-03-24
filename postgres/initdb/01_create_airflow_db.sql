SELECT 'CREATE DATABASE airflow' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'airflow')\gexec
