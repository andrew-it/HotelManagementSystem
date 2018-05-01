import psycopg2
from flask import g


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

    def insert_sys_user(self, email: str, password: str) -> [None, int]:
        try:
            cur = self.__get_cursor(self.ROLE_ADMIN)
            cur.execute("INSERT INTO sys_user (email, password, role) VALUES (%s, %s, %s) RETURNING user_id;",
                        (email, password, self.ROLE_ADMIN))
            g.db.commit()
            return cur.fetchone()['user_id']
        except psycopg2.IntegrityError:
            g.db.rollback()
            return None

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

    def get_cost_by_id(self, id):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute("SELECT cost FROM room WHERE room_id=%s", (id,))
        g.db.commit()
        return cur.fetchone()['cost']

    def create_transaction_get_id(self, info):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        cur.execute(
            "INSERT INTO transaction VALUES (DEFAULT, %(customer_id)s, %(payment_info)s, %(amount)s) RETURNING transaction_id;",
            info)
        g.db.commit()
        return cur.fetchone()['transaction_id']

class PostgresDatabase(Database):
    def method(self):
        # TODO
        pass


class DummyDatabase(Database):
    def method(self):
        # TODO
        pass
