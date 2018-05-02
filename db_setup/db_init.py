import os
import psycopg2

options = os.getenv("HMS_DB", "dbname=hms user=postgres password=postgres host=127.0.0.1")

connection = psycopg2.connect(options)
cursor = connection.cursor()
cursor.execute('''DROP SCHEMA public CASCADE;
               CREATE SCHEMA public;
               GRANT ALL ON SCHEMA public TO postgres;
               GRANT ALL ON SCHEMA public TO public;
               COMMENT ON SCHEMA public IS 'standard public schema'; ''')

schema = open('db_create.sql', "r").read()
cursor.execute(schema)

connection.commit()
