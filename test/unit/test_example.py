import allure


def test_foo():
    with allure.step('step one'):
        assert (True == True)

    with allure.step('step two'):
        assert (False == False)
