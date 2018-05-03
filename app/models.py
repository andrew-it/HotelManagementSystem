import logging

logger = logging.getLogger(__name__)


class User(object):

    def __init__(self, user_id, email, password, role):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.role == 'admin'

    def is_hotel_admin(self):
        return self.role == 'hotel_admin'

    def is_receptionist(self):
        return self.role == 'receptionist'

    def is_customer(self):
        return self.role == 'customer'

    def get_id(self):
        return str(self.user_id)


class AnonymousUser(object):

    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return True

    def is_admin(self):
        return False

    def is_hotel_admin(self):
        return False

    def is_receptionist(self):
        return False

    def is_customer(self):
        return False

    def get_id(self):
        return None


class Customer(object):

    def __init__(self, first_name, last_name, email, phone_number, payment_info):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.payment_info = payment_info


class HotelAdmin(object):

    def __init__(self, first_name, last_name, email, phone_number):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
