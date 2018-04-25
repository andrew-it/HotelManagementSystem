import psycopg2

connection = psycopg2.connect(dbname='hms', user='postgres', password='postgres', host='localhost', port='5432')
cursor = connection.cursor()
cursor.execute('''DROP SCHEMA public CASCADE;
               CREATE SCHEMA public;
               GRANT ALL ON SCHEMA public TO postgres;
               GRANT ALL ON SCHEMA public TO public;
               COMMENT ON SCHEMA public IS 'standard public schema'; ''')

schema = open('db_create.sql', "r").read()
cursor.execute(schema)

connection.commit()
