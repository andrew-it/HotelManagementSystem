import nose

def test_foo():
    with nose.allure.step('step one'):
        assert(True == True)

    with nose.allure.step('step two'):
        assert(False == False)

    with nose.allure.step('step three'):
        assert(2 == 0)