import allure
from app import bcrypt
from app.views import imgName, reverseDate, check_password
from time import time

@allure.feature('Helpers')
def test_check_password():
    """Test that checking password against it's hash works correctly"""

    password = "12345678"
    hash = bcrypt.generate_password_hash(password).decode('utf-8')

    with allure.step('Check valid password'):
        assert(check_password(hash, password) is True)

    with allure.step('[NEGATIVE] Check invalid password'):
        assert (check_password(hash, "invalid") is False)

    with allure.step('[NEGATIVE] Check valid password with invalid hash'):
        failed = False
        try:
            check_password("invalid", password)
        except:
            failed = True
        assert (failed is True)

    with allure.step('[NEGATIVE] Check invalid password with invalid hash'):
        failed = False
        try:
            check_password("invalid", "invalid")
        except:
            failed = True
        assert (failed is True)


@allure.feature('Helpers')
def test_img_name():
    """Test that image name generation works correctly"""

    def check_extension(original, output):
        orig_ext = original.rsplit('.', 1)[1]
        out_ext = output.rsplit('.', 1)[1]

        if orig_ext != out_ext:
            print("extensions are not equal")

        return orig_ext == out_ext

    def get_time(output):
        return output.rsplit('.', 1)[0]

    img_name = "file.png"

    with allure.step('Check that extension transfer is correct'):
        assert (check_extension(img_name, imgName(img_name)))

    with allure.step('Check that imgName allows image file extensions'):
        assert (imgName("file.png") is not None)
        assert (imgName("file.jpg") is not None)
        assert (imgName("file.jpeg") is not None)

    with allure.step('Check that imgName declines non-image file extensions'):
        assert (imgName("file.txt") is None)
        assert (imgName("file.pdf") is None)
        assert (imgName("file.docx") is None)

    with allure.step('Check that imgName timestamp is in past'):
        output = imgName(img_name)
        now = time()
        output_time = float(get_time(output))
        assert (output_time < now)

    with allure.step('Check that imgName timestamp is in immediate past'):
        output = imgName(img_name)
        now = time()
        output_time = float(get_time(output))
        assert (now - output_time < 1.0)


@allure.feature('Helpers')
def test_reverse_date():
    """Test that reversing date method works correctly"""

    with allure.step('Check that dash-separated date reverses'):
        assert (reverseDate("2018-01-03") == "03-01-2018")

    with allure.step('Check that month-day reverses correctly'):
        assert (reverseDate("01-03") == "03-01")

    with allure.step('Check that other input is not reversed'):
        assert (reverseDate("other") == "other")
