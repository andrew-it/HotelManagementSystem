import nose
from app.models import User, AnonymousUser, Customer, HotelAdmin

user_id = "user_id"
email = "user_email@example.com"
password = "12345678"


def create_user(role="querty"):
    return User(user_id, email, password, role)


@nose.allure.feature('Initialization')
def test_user_init():
    """Test that User object is initialized correctly"""
    with nose.allure.step('Create user'):
        user = create_user()

    with nose.allure.step('Check user ID'):
        assert(user.get_id() == user_id)

    with nose.allure.step('Check user email'):
        assert(user.email == email)

    with nose.allure.step('Check user password'):
        assert(user.password == password)


@nose.allure.feature('Status')
def test_user_status():
    """Check status-marking methods for a signed-in user"""
    with nose.allure.step('Initialize user'):
        user = create_user()

    with nose.allure.step('Check that a user is active'):
        assert (user.is_active())

    with nose.allure.step('Check that a user is authenticated'):
        assert (user.is_authenticated())

    with nose.allure.step('Check that a user is not anonymous'):
        assert (not user.is_anonymous())


@nose.allure.feature('Status')
def test_anonymous_user_status():
    """Check status-marking methods for an anonymous user"""
    with nose.allure.step('Initialize user'):
        user = AnonymousUser()

    with nose.allure.step('Check that a user is not active'):
        assert (not user.is_active())

    with nose.allure.step('Check that a user is not authenticated'):
        assert (not user.is_authenticated())

    with nose.allure.step('Check that a user is anonymous'):
        assert (user.is_anonymous())

    with nose.allure.step('Check that a user has no user ID'):
        assert (user.get_id() is None)


@nose.allure.feature('Role')
def test_customer_role():
    """Check role-determining methods for a user with a customer role"""
    with nose.allure.step('Initialize user'):
        user = create_user("customer")

    with nose.allure.step('Check that a user is a customer'):
        assert (user.is_customer())

    with nose.allure.step('Check that a user is not an admin'):
        assert (not user.is_admin())

    with nose.allure.step('Check that a user is not a hotel admin'):
        assert (not user.is_hotel_admin())

    with nose.allure.step('Check that a user is not a receptionist'):
        assert (not user.is_receptionist())


@nose.allure.feature('Role')
def test_hotel_admin_role():
    """Check role-determining methods for a user with a hotel admin role"""
    with nose.allure.step('Initialize user'):
        user = create_user("hotel_admin")

    with nose.allure.step('Check that a user is not a customer'):
        assert (not user.is_customer())

    with nose.allure.step('Check that a user is not an admin'):
        assert (not user.is_admin())

    with nose.allure.step('Check that a user is a hotel admin'):
        assert (user.is_hotel_admin())

    with nose.allure.step('Check that a user is not a receptionist'):
        assert (not user.is_receptionist())


@nose.allure.feature('Role')
def test_admin_role():
    """Check role-determining methods for a user with an admin role"""
    with nose.allure.step('Initialize user'):
        user = create_user("admin")

    with nose.allure.step('Check that a user is not a customer'):
        assert (not user.is_customer())

    with nose.allure.step('Check that a user is an admin'):
        assert (user.is_admin())

    with nose.allure.step('Check that a user is not a hotel admin'):
        assert (not user.is_hotel_admin())

    with nose.allure.step('Check that a user is not a receptionist'):
        assert (not user.is_receptionist())


@nose.allure.feature('Role')
def test_receptionist_role():
    """Check role-determining methods for a user with a receptionist role"""
    with nose.allure.step('Initialize user'):
        user = create_user("receptionist")

    with nose.allure.step('Check that a user is not a customer'):
        assert (not user.is_customer())

    with nose.allure.step('Check that a user is not an admin'):
        assert (not user.is_admin())

    with nose.allure.step('Check that a user is not a hotel admin'):
        assert (not user.is_hotel_admin())

    with nose.allure.step('Check that a user is a receptionist'):
        assert (user.is_receptionist())


@nose.allure.feature('Role')
def test_broken_role():
    """Check role-determining methods for a user with an invalid role"""
    with nose.allure.step('Initialize user'):
        user = create_user()

    with nose.allure.step('Check that a user is not a customer'):
        assert (not user.is_customer())

    with nose.allure.step('Check that a user is not an admin'):
        assert (not user.is_admin())

    with nose.allure.step('Check that a user is not a hotel admin'):
        assert (not user.is_hotel_admin())

    with nose.allure.step('Check that a user is not a receptionist'):
        assert (not user.is_receptionist())


@nose.allure.feature('Role')
def test_anonymous_user_role():
    """Check role-determining methods for an anonymous user"""
    with nose.allure.step('Initialize user'):
        user = create_user()

    with nose.allure.step('Check that a user is not a customer'):
        assert (not user.is_customer())

    with nose.allure.step('Check that a user is not an admin'):
        assert (not user.is_admin())

    with nose.allure.step('Check that a user is not a hotel admin'):
        assert (not user.is_hotel_admin())

    with nose.allure.step('Check that a user is not a receptionist'):
        assert (not user.is_receptionist())

@nose.allure.feature('Initialization')
def test_customer():
    """Test that Customer object is initialized correctly"""
    first_name = "John"
    last_name = "Doe"
    email = "johndoe@example.com"
    phone_number = "123456789"
    payment_info = "mastercard"

    with nose.allure.step('Initialize customer'):
        customer = Customer(first_name, last_name, email, phone_number, payment_info)

    with nose.allure.step('Check first name'):
        assert(customer.first_name == first_name)

    with nose.allure.step('Check last name'):
        assert(customer.last_name == last_name)

    with nose.allure.step('Check email'):
        assert(customer.email == email)

    with nose.allure.step('Check phone number'):
        assert(customer.phone_number == phone_number)

    with nose.allure.step('Check payment info'):
        assert(customer.payment_info == payment_info)


@nose.allure.feature('Initialization')
def test_hotel_admin():
    """Test that HotelAdmin object is initialized correctly"""
    first_name = "John"
    last_name = "Doe"
    email = "johndoe@example.com"
    phone_number = "123456789"

    with nose.allure.step('Initialize hotel admin'):
        admin = HotelAdmin(first_name, last_name, email, phone_number)

    with nose.allure.step('Check first name'):
        assert (admin.first_name == first_name)

    with nose.allure.step('Check last name'):
        assert (admin.last_name == last_name)

    with nose.allure.step('Check email'):
        assert (admin.email == email)

    with nose.allure.step('Check phone number'):
        assert (admin.phone_number == phone_number)

