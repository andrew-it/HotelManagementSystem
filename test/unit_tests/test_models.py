import nose
from app.models import User

def test_user():
    user = None
    id = "user_id"
    email = "user_email@example.com"
    password = "12345678"
    role = "customer"

    with nose.allure.step('init user'):
        user = User(id, email, password, role)

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
