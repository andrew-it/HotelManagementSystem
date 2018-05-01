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
                (user_id, f_name l_name, phone_number))
            g.db.commit()
        except Exception as e:
            print(e)

    def get_all_hotels(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT COUNT(*) as hotels FROM hotel")
        return cur.fetchone()['hotels']

    def get_all_system_users(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT COUNT(*) as users FROM sys_user")
        return cur.fetchone()['users']

    def get_db_statistics(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute("SELECT blks_hit::float/(blks_read + blks_hit) as cache_hit_ratio, "
                    "numbackends FROM pg_stat_database WHERE datname='hms'")
        return dict(cur.fetchall()[0])

    def get_all_admins(self):
        cur = self.__get_cursor(self.ROLE_ADMIN)
        cur.execute(f"SELECT * FROM admin NATURAL JOIN sys_user WHERE role={self.ROLE_ADMIN}")
        return cur.fetchall()

    def get_rooms_by_params(self, recep, checkin_date, chechout_date):
        cur = self.__get_cursor(self.ROLE_CUSTOMER)
        query = "SELECT * FROM room r INNER JOIN room_config rc ON (r.config_id=rc.config_id) INNER JOIN room_option ro ON (r.option_id=ro.option_id) WHERE r.hotel_id=%s AND r.quantity > (SELECT coalesce(MAX(b.quantity), 0) FROM booking b WHERE r.room_id = b.room_id AND NOT (%s <= b.checkin_date OR %s >= b.checkout_date))"
        cur.execute(query, (recep, checkin_date, chechout_date))
        rooms = cur.fetchall()
        g.db.commit()
        return rooms


class PostgresDatabase(Database):
    def method(self):
        # TODO
        pass


class DummyDatabase(Database):
    def method(self):
        # TODO
        pass
