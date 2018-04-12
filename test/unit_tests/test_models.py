import nose
from app.models import User, AnonymousUser, Customer, HotelAdmin


def test_user():
    user = None
    id = "user_id"
    email = "user_email@example.com"
    password = "12345678"
    role = "customer"

    with nose.allure.step('init user'):
        user = User(id, email, password, role)
        assert(user.get_id() == id)
        assert(user.email == email)
        assert(user.password == password)
        assert(user.role == role)

    with nose.allure.step('status'):
        assert(user.is_active())
        assert(user.is_authenticated())
        assert(not user.is_anonymous())

    with nose.allure.step("role"):
        user.role = "customer"
        assert(user.is_customer())
        assert(not user.is_admin())
        assert(not user.is_hotel_admin())
        assert(not user.is_receptionist())

        user.role = "hotel_admin"
        assert(user.is_hotel_admin())
        assert(not user.is_customer())
        assert(not user.is_admin())
        assert(not user.is_receptionist())

        user.role = "admin"
        assert(user.is_admin())
        assert(not user.is_customer())
        assert(not user.is_hotel_admin())
        assert(not user.is_receptionist())

        user.role = "receptionist"
        assert(user.is_receptionist())
        assert(not user.is_customer())
        assert(not user.is_admin())
        assert(not user.is_hotel_admin())


def test_anonymous_user():
    user = AnonymousUser()
    assert(not user.is_authenticated())
    assert(not user.is_active())
    assert(user.is_anonymous())
    assert(not user.is_admin())
    assert(not user.is_hotel_admin())
    assert(not user.is_receptionist())
    assert(not user.is_customer())
    assert(user.get_id() is None)


def test_customer():
    first_name = "John"
    last_name = "Doe"
    email = "johndoe@example.com"
    phone_number = "123456789"
    payment_info = "mastercard"

    with nose.allure.step('init customer'):
        customer = Customer(first_name, last_name, email, phone_number, payment_info)
        assert(customer.first_name == first_name)
        assert(customer.last_name == last_name)
        assert(customer.email == email)
        assert(customer.phone_number == phone_number)
        assert(customer.payment_info == payment_info)


def test_hotel_admin():
    first_name = "John"
    last_name = "Doe"
    email = "johndoe@example.com"
    phone_number = "123456789"

    with nose.allure.step('init customer'):
        admin = HotelAdmin(first_name, last_name, email, phone_number)
        assert (admin.first_name == first_name)
        assert (admin.last_name == last_name)
        assert (admin.email == email)
        assert (admin.phone_number == phone_number)

