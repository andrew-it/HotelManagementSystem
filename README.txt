You need install:
-postgresql==9.5.5
-requirements for python 3.4 from requirements.txt
-create database:
    name:       hms
    user:       admin
    password:   admin
-run db_create.sql in your database to build database
-run db_sql.sql in your database to insert data
-in folder with run.py execute in command line  "export FLASK_APP=run.py"
-execute in command line: "flask run" to start server
-IN THE SYSTEM THERE ARE DEFAULT ADMIN USER:
	email: admin
	password: admin

- FOR CREATE DB AND FILL IT YOU NEED:
1) RUN: db_create.sql on PostgreSQL
2) RUN: /data_generator/generateSQL.py(better) OR /data_generator/db_data.sql
there is more than 1 million tuples