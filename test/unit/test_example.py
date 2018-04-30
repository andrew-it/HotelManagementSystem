import nose


@nose.allure.feature("Example Test Feature")
def test_one():
    """This is Test Description"""
    with nose.allure.step('step one'):
        assert(True == True)

    with nose.allure.step('step two'):
        assert(False == False)


@nose.allure.feature("Example Test Feature")
def test_two():
    """This is Test Description"""
    with nose.allure.step('step one'):
        assert(True == True)

    with nose.allure.step('step two'):
        assert(False == False)


@nose.allure.story("Example Test Story")
def test_three():
    """This is Test Description"""
    with nose.allure.step('step one'):
        assert(True == True)


@nose.allure.story("Example Test Story")
def test_four():
    """This is Test Description"""
    with nose.allure.step('step one'):
        assert(True == True)