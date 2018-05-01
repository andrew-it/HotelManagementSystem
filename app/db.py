import psycopg2
from flask import g


def searchOp(args):
    d = ['is_bathroom', 'is_tv', 'is_wifi', 'is_bathhub', 'is_airconditioniring']
    s = []
    for key in d:
        if args[key]:
            line = 'ro.' + key + '=%(' + key + ')s'
            s.append(line)
    s = ' AND '.join(s)
    return '(' + s + ')'


class Database:
    def method(self):
        pass


class AndrewDB(Database):
    ROLE_ADMIN = 'admin'
    ROLE_CUSTOMER = 'costomer'
    ROLE_HOTEL_ADMIN = 'hotel_admin'
    ROLE_RECEPTIONIST = 'receptionist'

    def __connect_to_db(self):
        connection = "dbname=hms user=postgres password=postgres host='0.0.0.0'"
        try:
            return psycopg2.connect(connection)
        except Exception:
            print("Can't connect to database")

    def __get_cursor(self, role: str):
        dict_cursor = psycopg2.extras.DictCursor
        g.db = self.__connect_to_db()
        g.role = role
        return g.db.cursor(cursor_factory=dict_cursor)

    def insert_sys_user_get_id(self, email: str, password: str) -> [None, int]:
        res = self.insert_sys_user(email, password)
        if res:
            return res['user_id']
        else:
            return None

    def insert_sys_user(self, email: str, password: str):
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING user_id;",
                        (email, password, self.ROLE_ADMIN))
            g.db.commit()
            return cur.fetchone()
        except psycopg2.IntegrityError:
            g.db.rollback()
            return None

    def get_sys_user_by_email(self, email):
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute("SELECT * FROM sys_user WHERE email=%s;", (email,))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()

    def insert_admin(self, user_id: str, f_name: str, l_name: str, phone_number: str) -> None:
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute(
                "INSERT INTO admin (person_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s);",
                (user_id, f_name, l_name, phone_number))
            g.db.commit()
        except Exception as e:
            print(e)

    def get_all_hotels(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT COUNT(*) as hotels FROM hotel")
        g.db.commit()
        return cur.fetchone()['hotels']

    def get_all_system_users(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT COUNT(*) as users FROM sys_user")
        g.db.commit()
        return cur.fetchone()['users']

    def get_db_statistics(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT blks_hit::float/(blks_read + blks_hit) as cache_hit_ratio, "
                    "numbackends FROM pg_stat_database WHERE datname='hms'")
        g.db.commit()
        return dict(cur.fetchall()[0])

    def get_all_admins(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute(f"SELECT * FROM admin NATURAL JOIN sys_user WHERE role={self.ROLE_ADMIN}")
        g.db.commit()
        return cur.fetchall()

    def get_rooms_by_params(self, recep, checkin_date, chechout_date):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        query = "SELECT * " \
                "FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) " \
                "INNER JOIN room_option ro ON (r.option_id=ro.option_id) " \
                "WHERE r.hotel_id=%s AND r.quantity > " \
                "(SELECT coalesce(MAX(b.quantity), 0) FROM booking b " \
                "WHERE r.room_id = b.room_id AND NOT (%s <= b.checkin_date OR %s >= b.checkout_date))"
        cur.execute(query, (recep, checkin_date, chechout_date))
        rooms = cur.fetchall()
        g.db.commit()
        return rooms

    def get_all_receptionists(self, user_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM receptionist WHERE person_id=%s", (user_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_vw_hotel_by_id(self, hotel_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM vw_hotels WHERE hotel_id=%s", (hotel_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_vw_customer_by_id(self, person_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM vw_customers WHERE person_id=%s", (person_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_customer_by_id(self, person_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM customers WHERE person_id=%s", (person_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_hotel_admin_by_id(self, person_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM hotel_admin WHERE person_id=%s", (person_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_receptionist_by_id(self, person_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM receptionist WHERE person_id=%s", (person_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_admin_by_id(self, person_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM admin WHERE person_id=%s", (person_id,))
        g.db.commit()
        return dict(cur.fetchone())

    def get_hotel_by_id(self, hotel_id):
        try:
            cur = self.__get_cursor(self.ROLE_CUSTOMER)
            cur.execute("SELECT * FROM hotel WHERE hotel_id=%s;", (hotel_id,))
            g.db.commit()
            return cur.fetchone()
        except Exception as e:
            print(e)
            return None

    def get_rooms_with_settings_by_id(self, hotel_id):
        try:
            cur = self.__get_cursor(self.ROLE_CUSTOMER)
            cur.execute(
                "SELECT * FROM room r, room_config rc, room_option ro "
                "WHERE r.hotel_id=%s AND r.config_id=rc.config_id AND r.option_id=ro.option_id;",
                (hotel_id,))
            return cur.fetchall()
        except Exception as e:
            print(e)
            return None

    def get_booked_rooms_by_hotel_id(self, hotel_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT * FROM vw_booked_rooms WHERE hotel_id=%s", (hotel_id,))
        g.db.commit()
        return cur.fetchall()

    def delete_transaction(self, transaction_id) -> bool:
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute("DELETE FROM transaction WHERE transaction_id=%s", (transaction_id,))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_some_info_by_user_id(self, user_id):
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute(
                "SELECT *, b.quantity as booked "
                "FROM booking b INNER JOIN transaction t ON (b.transaction_id=t.transaction_id) "
                "INNER JOIN room r ON (b.room_id=r.room_id) INNER JOIN room_option ro ON (r.option_id=ro.option_id) "
                "INNER JOIN hotel h ON (h.hotel_id=r.hotel_id) INNER JOIN country c ON (h.city=c.city) "
                "WHERE b.customer_id=%s",
                (user_id,))
            g.db.commit()
            return cur.fetchall()
        except Exception as e:
            print(e)
        return None

    def get_option_by_params(self, is_bath, is_tv, is_wifi, is_bathh, is_air):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "SELECT option_id FROM room_option "
                "WHERE is_bathroom=%s AND is_tv=%s AND is_wifi=%s AND is_bathhub=%s AND is_airconditioniring=%s;",
                (is_bath, is_tv, is_wifi, is_bathh, is_air))
            g.db.commit()
            return cur.fetchone()
        except Exception as e:
            print(e)
            return None

    def insert_option(self, is_bath, is_tv, is_wifi, is_bathh, is_air):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "INSERT INTO room_option (is_bathroom, is_tv, is_wifi, is_bathhub, is_airconditioniring) "
                "VALUES (%s, %s, %s, %s, %s) RETURNING option_id;",
                (is_bath, is_tv, is_wifi, is_bathh, is_air))
            g.db.commit()
            return cur.fetchone()['option_id']
        except Exception as e:
            print(e)
            return None

    def delete_room_by_id(self, room_id) -> bool:
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute("DELETE FROM room WHERE room_id=%s;", (room_id,))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def select_config(self, single_bed, souble_bed, sofa_bed):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "SELECT config_id FROM room_config WHERE single_bed=%s AND double_bed=%s AND sofa_bed=%s;",
                (single_bed, souble_bed, sofa_bed))
            g.db.commit()
            return cur.fetchone()
        except Exception as e:
            print(e)
            return None

    def insert_config(self, single_bed, souble_bed, sofa_bed):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "INSERT INTO room_config (single_bed, double_bed, sofa_bed) VALUES (%s, %s, %s) RETURNING config_id;",
                (single_bed, souble_bed, sofa_bed))
            g.db.commit()
            return cur.fetchone()['config_id']
        except Exception as e:
            print(e)
            return None

    def set_up_room_by_id(self, config_id, option_id, quantity, title, description, cost, room_id):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "UPDATE room SET (config_id, option_id, quantity, title, description, cost)=(%s, %s, %s, %s, %s, %s) "
                "WHERE room_id=%s;",
                (config_id, option_id, quantity, title, description, cost, room_id))
            g.db.commit()
        except Exception as e:
            print(e)

    def delete_receptionist_by_id(self, recep_id) -> bool:
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute("DELETE FROM sys_user WHERE user_id=%s;", (recep_id,))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def insert_user(self, email, password, role):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING user_id;",
                        (email, password, role))
            g.db.commit()
            return cur.fetchone()['user_id']
        except psycopg2.IntegrityError:
            g.db.rollback()
            return None

    def add_new_receptionist(self, user_id, hotel_id, f_name, l_name, phone) -> bool:
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "INSERT INTO receptionist (person_id, hotel_id, first_name, last_name, phone_number, salary) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (user_id, hotel_id, f_name, l_name, phone))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def add_new_room(self, hotel_id, config_id, option_id, quantity, title, descr, cost):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute(
                "INSERT INTO room (hotel_id, config_id, option_id, quantity, title, description, cost) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s);",
                (hotel_id, config_id, option_id, quantity, title, descr, cost))
            g.db.commit()
        except Exception as e:
            print(e)

    def get_receptionists_by_hotel_id(self, hotel_id):
        try:
            cur = self.__get_cursor(self.ROLE_RECEPTIONIST)
            cur.execute("SELECT * FROM sys_user u, receptionist r WHERE u.user_id=r.person_id AND r.hotel_id=%s;",
                        (hotel_id,))
            g.db.commit()
            return cur.fetchall()
        except Exception as e:
            print(e)
            return None

    def get_cost_by_id(self, id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT cost FROM room WHERE room_id=%s", (id,))
        g.db.commit()
        return cur.fetchone()['cost']

    def create_transaction_get_id(self, info):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute(
            "INSERT INTO transaction VALUES (DEFAULT, %(customer_id)s, %(payment_info)s, %(amount)s) "
            "RETURNING transaction_id;",
            info)
        g.db.commit()
        return cur.fetchone()['transaction_id']

    def insert_location_if_not_exists(self, country, city):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT * FROM country WHERE country=%s AND city=%s;", (country, city))
        g.db.commit()
        if not cur.fetchone():
            cur.execute("INSERT INTO country (country, city) VALUES (%s, %s);", (country, city))
            g.db.commit()

    def add_hotel(self, city, address, name, stars, description, owner_id, img):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute(
            "INSERT INTO hotel (city, address, name, stars, description, owner_id, img) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (city, address, name, stars, description, owner_id, img))
        g.db.commit()

    def get_city(self, country, city):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        try:
            cur.execute("SELECT * FROM country WHERE country=%s AND city=%s;", (country, city))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()

    def add_city(self, country, city) -> bool:
        cur = self.__get_cursor(self.ROLE_ADMIN)
        try:
            cur.execute("INSERT INTO country (country, city) VALUES (%s, %s);",
                        (country, city))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_image_name_by_hotel_id(self, hotel_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        try:
            cur.execute("SELECT img FROM hotel WHERE hotel_id=%s;", (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()['img']

    def update_hotel_by_id(self, hotel_id, city, address, hotel_name, stars, description, img_path) -> bool:
        cur = self.__get_cursor(self.ROLE_ADMIN)
        try:
            cur.execute(
                "UPDATE hotel SET (city, address, name, stars, description, img)=(%s, %s, %s, %s, %s, %s) "
                "WHERE hotel_id=%s;",
                (city, address, hotel_name, stars, description, img_path, hotel_id))
            g.db.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_hotel_and_address_by_id(self, hotel_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        try:
            cur.execute("SELECT * FROM hotel h, country c WHERE hotel_id=%s AND h.city=c.city;", (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()

    def add_booking(self, info):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        try:
            cur.execute(
                "INSERT INTO booking "
                "VALUES (%(room_id)s, %(customer_id)s, %(transaction_id)s, %(quantity)s, %(checkin)s, %(checkout)s)",
                info)
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()

    def search_get_rooms(self, search):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        query = "SELECT * FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) " \
                "INNER JOIN room_option ro ON (r.option_id=ro.option_id) " \
                "WHERE r.hotel_id=%(hotel_id)s AND r.quantity > (SELECT coalesce(MAX(b.quantity), 0) " \
                "FROM booking b WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date " \
                "OR %(checkin)s >= b.checkout_date)) AND r.quantity >= %(quantity)s " \
                "AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s)"
        if search['is_bathroom'] or \
                search['is_tv'] or \
                search['is_wifi'] or \
                search['is_bathhub'] or \
                search['is_airconditioniring']:
            options = searchOp(search)
            query += " AND " + options
        if search['price_to'] != 0:
            query += " AND (%(price_from)s <= r.cost AND %(price_to)s >= r.cost)"
        try:
            cur.execute(query, search)
            g.db.commit()
        except Exception as e:
            print(e)
        cur.fetchall()

    def add_customer(self, person_id, first_name, last_name, phone_number):
        try:
            cur = self.__get_cursor(self.ROLE_CUSTOMER)
            cur.execute(
                "INSERT INTO customer (person_id, first_name, last_name, phone_number) VALUES (%s, %s, %s, %s);",
                (person_id, first_name, last_name, phone_number))
            g.db.commit()
        except Exception as e:
            print(e)

    def update_customer(self, person_id, first_name, last_name, phone_number, payment_info):
        try:
            cur = self.__get_cursor(self.ROLE_CUSTOMER)
            cur.execute(
                "UPDATE customer SET (first_name, last_name, phone_number, payment_info)=(%s, %s, %s, %s) "
                "WHERE person_id=%s;",
                (person_id, first_name, last_name, phone_number, payment_info))
            g.db.commit()
        except Exception as e:
            print(e)

    def update_hotel_admin(self, person_id, first_name, last_name, phone_number):
        try:
            cur = self.__get_cursor(self.ROLE_HOTEL_ADMIN)
            cur.execute(
                "UPDATE hotel_admin SET (first_name, last_name, phone_number)=(%s, %s, %s) WHERE person_id=%s;",
                (first_name, last_name, phone_number, person_id))
            g.db.commit()
        except Exception as e:
            print(e)

    def update_admin(self, person_id, first_name, last_name, phone_number):
        try:
            cur = self.__get_cursor(self.ROLE_HOTEL_ADMIN)
            cur.execute(
                "UPDATE admin SET (first_name, last_name, phone_number)=(%s, %s, %s) WHERE person_id=%s;",
                (first_name, last_name, phone_number, person_id))
            g.db.commit()
        except Exception as e:
            print(e)

    def search_hotels_by_form(self, search):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        query = "SELECT * FROM hotel h INNER JOIN country c ON (h.city=c.city) AND (lower(h.city) " \
                "LIKE %(destination)s OR lower(c.country) LIKE %(destination)s " \
                "OR lower(h.name) LIKE %(destination)s) AND EXISTS(SELECT r.hotel_id " \
                "FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) " \
                "WHERE r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b " \
                "WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date " \
                "OR %(checkin)s >= b.checkout_date)) AND r.quantity >= %(quantity)s " \
                "AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s)"
        if search['is_bathroom'] or \
                search['is_tv'] or \
                search['is_wifi'] or \
                search['is_bathhub'] or \
                search['is_airconditioniring']:
            options = searchOp(search)
            query = "SELECT * FROM hotel h, country c WHERE h.city = c.city AND (lower(h.city) " \
                    "LIKE %(destination)s OR lower(c.country) LIKE %(destination)s OR lower(h.name) " \
                    "LIKE %(destination)s) AND EXISTS(SELECT r.hotel_id FROM room r, room_config rc, room_option ro " \
                    "WHERE r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b " \
                    "WHERE r.room_id = b.room_id AND NOT (%(checkout)s <= b.checkin_date " \
                    "OR %(checkin)s >= b.checkout_date)) AND r.config_id=rc.config_id " \
                    "AND r.option_id=ro.option_id AND r.quantity >= %(quantity)s " \
                    "AND (rc.single_bed + 2 * rc.double_bed + rc.sofa_bed >= %(sleeps)s) AND " + options
        if search['price_to'] != 0:
            query += " AND (%(price_from)s <= r.cost AND %(price_to)s >= r.cost)"
        query += ")"
        cur.execute(query, search)
        g.db.commit()
        return cur.fetchall()

    def get_user_by_id(self, user_id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        try:
            cur.execute("SELECT * FROM sys_user WHERE user_id=%s;", (user_id,))
        except Exception as e:
            print(e)
        g.db.commit()
        return cur.fetchone()

    def remove_hotel_by_id(self, hotel_id):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        try:
            cur.execute("DELETE FROM hotel WHERE hotel_id=%s RETURNING img;", (hotel_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchone()['img']

    def get_hotels_by_admin_id(self, user_id):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        try:
            cur.execute("SELECT * FROM hotel h, country c WHERE owner_id=%s AND h.city=c.city;",
                        (user_id,))
            g.db.commit()
        except Exception as e:
            print(e)
        return cur.fetchall()


class PostgresDatabase(Database):
    def method(self):
        # TODO
        pass


class DummyDatabase(Database):
    def method(self):
        # TODO
        pass
