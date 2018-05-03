import json
import random
import re
import time
import os

import psycopg2
import psycopg2.extras

START_TIME = time.time()

def connectToDB():
    options = os.getenv("HMS_DB", "dbname=hms user=postgres password=postgres host=127.0.0.1")
    return psycopg2.connect(options)


def wrapper(str):
    return "'" + str + "'"


def readFromFile(filename):
    with open(filename, 'r') as f:
        tmp = []
        for line in f:
            line = re.sub("'", "", line)
            if not (line in tmp):
                tmp.append(line)
    print("Unique lines in " + filename + " = " + str(len(tmp)))
    with open(filename, 'w') as f:
        f.write("".join(tmp))
    return tmp


customerCount = 0
sys_userCount = 0
cities_name = []
hotel_admins_id = []
hotels_id = []
options_id = []
config_id = []


def countryGenerator():
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    f = open("country.json", 'r')
    country = f.read()
    country = json.loads(country)
    f.close()
    f = open("country.sql", 'a')
    for i in range(len(country)):
        country_query = "INSERT INTO country VALUES (" + "'" + country[i]['country'] + "','" + country[i][
            'city'] + "');\n"
        cities_name.append(country[i]['city'])
        cur.execute(country_query)
        # print(country_query)
        f.writelines(country_query)
    f.close()
    db.commit()
    db.close()


def customersGenereator(times):
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    emails = None
    with open('sys_user.json', 'r') as f:
        emails = f.read()
    emails = json.loads(emails)
    with open('customers.json', 'r') as f:
        customers = f.read()
    customers = json.loads(customers)
    with open('customers.sql', 'a') as f:
        for k in range(0, times):
            for i in range(len(emails)):
                global customerCount
                global sys_userCount
                customerCount += 1
                sys_userCount += 1
                sys_user_query = "INSERT INTO sys_user VALUES (DEFAULT, '" + str(k) + emails[i][
                    'email'] + "', '$2b$12$tdsR.Lae9t0WaqDGwlF39.0BVMEAKQae1DF24tt.h6VI0OSyGIZHO', 'customer') RETURNING user_id;\n"
                cur.execute(sys_user_query)
                customers[i]['user_id'] = str(cur.fetchone()['user_id'])
                f.writelines(sys_user_query)
                customer_qurey = "INSERT INTO customer VALUES (" + "'" + customers[i]['user_id'] + "','" + customers[i][
                    'first_name'] + "','" + customers[i]['last_name'] + "','" + customers[i]['phone_number'] + "','" + \
                                 customers[i]['payment_info'] + "'"');\n'
                cur.execute(customer_qurey)
                f.writelines(customer_qurey)
    db.commit()
    db.close()


def hotel_adminsGenerator():
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    emails = None
    with open('sys_user.json', 'r') as f:
        emails = f.read()
    emails = json.loads(emails)
    with open('customers.json', 'r') as f:
        admins = f.read()
    admins = json.loads(admins)
    with open('hotel_admin.sql', 'a') as f:
        for i in range(len(emails)):
            sys_user_query = "INSERT INTO sys_user VALUES (DEFAULT, '" + emails[i][
                'email'] + "', '$2b$12$tdsR.Lae9t0WaqDGwlF39.0BVMEAKQae1DF24tt.h6VI0OSyGIZHO', 'hotel_admin') RETURNING user_id;\n"
            cur.execute(sys_user_query)
            admins[i]['user_id'] = str(cur.fetchone()['user_id'])
            hotel_admins_id.append(admins[i]['user_id'])
            f.writelines(sys_user_query)
            hotel_admin_query = "INSERT INTO hotel_admin VALUES (" + "'" + admins[i]['user_id'] + "','" + admins[i][
                'first_name'] + "','" + admins[i]['last_name'] + "','" + admins[i]['phone_number'] + "');\n"
            cur.execute(hotel_admin_query)
            f.writelines(hotel_admin_query)
            db.commit()


def optionsGenerator():
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    variants = ['True', 'False']
    with open('options.sql', 'a') as f:
        for wifi in range(2):
            for bath in range(2):
                for tv in range(2):
                    for hub in range(2):
                        for air in range(2):
                            option_query = "INSERT INTO room_option VALUES (DEFAULT ,'" + variants[bath] + "','" + \
                                           variants[tv] + "','" + variants[wifi] + "','" + variants[hub] + "','" + \
                                           variants[air] + "') RETURNING option_id;\n"
                            cur.execute(option_query)
                            tmp = cur.fetchone()['option_id']
                            options_id.append(tmp)
                            db.commit()
                            f.writelines(option_query)


def configGenerator():
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    with open('config.sql', 'a') as f:
        for double in range(2):
            for single in range(4):
                for sofa in range(2):
                    config_query = "INSERT INTO room_config VALUES (DEFAULT ,'" + str(double) + "','" + str(
                        single) + "','" + str(sofa) + "') RETURNING config_id;\n"
                    cur.execute(config_query)
                    tmp = cur.fetchone()['config_id']
                    config_id.append(tmp)
                    f.writelines(config_query)
                    db.commit()


def rooms_generator(hotel_id):
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    with open('room.json', 'r') as f:
        room = json.loads(f.read())
    with open('room.sql', 'a') as f:
        for i in range(len(room)):
            room_query = "INSERT INTO room VALUES (DEFAULT ,'" + str(
                hotel_id) + "','" + getRandomConfig() + "','" + getRandomOption() + "','" + getRandomQuantity() + "','" + \
                         room[i]['title'] + "','" + room[i]['description'] + "','" + getRandomCost() + "');\n";
            f.writelines(room_query)
            cur.execute(room_query)
            db.commit()


def hotels_Generator():
    db = connectToDB()
    cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    with open('hotel.json', 'r') as f:
        hotel = f.read()
    hotel = json.loads(hotel)
    with open('hotel.sql', 'a') as f:
        for i in range(len(hotel)):
            hotel_query = "INSERT INTO hotel VALUES (DEFAULT ,'" + getRandomCity() + "','" + hotel[i][
                'address'] + "','" + hotel[i]['name'] + "','" + getRandomStars() + "','" + hotel[i][
                              'description'] + "','" + getRandomImg() + "','" + getRandomOwner() + "') RETURNING hotel_id;\n"
            cur.execute(hotel_query)
            f.writelines(hotel_query)
            hotel_id = cur.fetchone()['hotel_id']
            hotels_id.append(hotel_id)
            db.commit()


######getters######
def getRandomOption():
    return str(options_id[random.randint(0, len(options_id) - 1)])


def getRandomConfig():
    return str(config_id[random.randint(0, len(config_id) - 1)])


def getRandomQuantity():
    return str(random.randint(1, 10))


def getRandomCost():
    return str(random.randint(1000, 3000))


def getRandomStars():
    return str(random.randint(1, 5))


def getRandomImg():
    imgs = ["/static/img/hotels/1.png",
            "/static/img/hotels/2.png",
            "/static/img/hotels/3.png",
            "/static/img/hotels/4.png",
            "/static/img/hotels/5.png",
            ]
    return imgs[random.randint(0, len(imgs) - 1)]


def getRandomCity():
    return cities_name[random.randint(0, len(cities_name) - 1)]


def getRandomOwner():
    return hotel_admins_id[random.randint(0, len(hotel_admins_id) - 1)]


###################

countryGenerator()
configGenerator()
optionsGenerator()
customersGenereator(1)
hotel_adminsGenerator()
hotels_Generator()
for hot in hotels_id:
    rooms_generator(hot)

with open("db_date.sql", 'a') as f:
    finalStr = open("country.sql", 'r').read()
    finalStr += open("config.sql", 'r').read()
    finalStr += open("options.sql", 'r').read()
    finalStr += open("customers.sql", 'r').read()
    finalStr += open("hotel_admin.sql", 'r').read()
    finalStr += open("hotel.sql", 'r').read()
    finalStr += open("room.sql", 'r').read()
    f.writelines(finalStr)

END_TIME = time.time()

FINAL_TIME = END_TIME - START_TIME
print("Time to generate = " + str(FINAL_TIME / 60) + " min.")
