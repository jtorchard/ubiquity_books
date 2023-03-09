import pytest
from books import create_app
from books.main import allowed_file, valid_isbn_10


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here


@pytest.fixture()
def valid_isbn10(app):
    return '1234567891'


@pytest.fixture()
def invalid_isbn10(app):
    return '123456789-123'


@pytest.fixture()
def valid_filename(app):
    return 'my_books.csv'


@pytest.fixture()
def valid_filename_double_extension(app):
    return 'my_books.eml.csv'


@pytest.fixture()
def invalid_filename(app):
    return 'my_books.mkv'


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_home_happy_path(client):
    response = client.get('/')
    assert b'Home Page' in response.data


def test_valid_file_is_true(valid_filename):
    assert allowed_file(valid_filename) is True


def test_valid_file_extra_extension_is_true(valid_filename_double_extension):
    assert allowed_file(valid_filename_double_extension) is True


def test_invalid_file_is_false(invalid_filename):
    assert allowed_file(invalid_filename) is False


def test_valid_isbn10_is_true(valid_isbn10):
    assert valid_isbn_10(valid_isbn10) is True


def test_invalid_isbn10_is_false(invalid_isbn10):
    assert valid_isbn_10(invalid_isbn10) is False
