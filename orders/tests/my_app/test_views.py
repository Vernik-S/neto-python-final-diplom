import pytest
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
import json
from django.http import QueryDict

from my_app.models import ConfirmEmailToken, User, Contact
from requests_toolbelt.multipart.encoder import MultipartEncoder
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_user_register(client):
    # Arrange
    test_email = "Test15@aaa.aa"
    data = {
        "first_name": "TName",
        "last_name": "TSurname",
        "email": test_email,
        "company": "TCompany",
        "password": "Q1W2E3aaa",
        "position": "Tposition"
    }

    json_data = json.dumps(data)

    # Act
    response = client.post(reverse("my_app:user-register"), data=json_data, follow=True,
                           content_type="application/json")

    # Assert
    data = response.json()
    assert data == {"Status": True}
    assert response.status_code == 200

    user = User.objects.get(email=test_email)
    try:
        email_token = ConfirmEmailToken.objects.get(user=user)
    except ConfirmEmailToken.DoesNotExist:
        email_token = None

    assert email_token


@pytest.fixture()
def test_password():
    return "Q1W2E3aaa"


@pytest.fixture()
def test_details():
    test_data = {
        "first_name": "TName",
        "last_name": "TSurname",
        "email": "Test20@aaa.aa",
        "company": "TCompany",
        # "password": "Q1W2E3aaa",
        "position": "Tposition"
    }

    return test_data


@pytest.fixture()
# @pytest.db
def test_user(test_password, test_details):
    # test_data = {
    #     "first_name": "TName",
    #     "last_name": "TSurname",
    #     "email": "Test20@aaa.aa",
    #     "company": "TCompany",
    #     #"password": "Q1W2E3aaa",
    #     "position": "Tposition"
    # }

    user = User.objects.get_or_create(**test_details)[0]

    user.set_password(test_password)
    user.save()
    return user


@pytest.mark.django_db
def test_user_confirm(client, test_user):
    # Arrange
    confirm_token, _ = ConfirmEmailToken.objects.get_or_create(user_id=test_user.id)
    email = test_user.email

    test_data = {
        "email": email,
        "token": confirm_token.key
    }

    # Act
    response = client.post(reverse("my_app:user-confirm"), data=json.dumps(test_data), follow=True,
                           content_type="application/json")
    data = response.json()
    test_user.refresh_from_db()

    # Assert
    assert data == {"Status": True}
    assert response.status_code == 200
    assert test_user.is_active


@pytest.fixture()
# @pytest.db
def test_user_active(test_user):
    test_user.is_active = True
    test_user.save()

    # all_users = User.objects.all().first()

    return test_user


@pytest.mark.django_db
def test_user_login(client, test_user_active, test_password):
    # Arrange

    test_data = {
        "email": test_user_active.email,
        "password": test_password
    }

    # Act
    response = client.post(reverse("my_app:user-login"), data=json.dumps(test_data), follow=True,
                           content_type="application/json")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data.get("Status") is True

    received_token = data.get("Token")
    test_user_token = Token.objects.get(user=test_user_active)

    assert received_token == test_user_token.key


@pytest.fixture
def auth_token(test_user_active):
    return Token.objects.get_or_create(user=test_user_active)[0]


@pytest.fixture
def authorized_client(client, auth_token, test_user_active):
    client.force_login(test_user_active)
    client.credentials(HTTP_AUTHORIZATION='Token ' + auth_token.key)

    return client


@pytest.mark.django_db
def test_user_get_details(client, auth_token, test_details, test_user_active, authorized_client):
    # Arrange
    # client.credentials(**{'Authorization': f'Token {auth_token.key}'})
    # client.force_login(test_user_active)
    # client.credentials(HTTP_AUTHORIZATION='Token ' + auth_token.key)

    # Act
    response = authorized_client.get(reverse("my_app:user-details"), follow=True,
                                     content_type="application/json", )  # HTTP_Authorization=f'Token {auth_token.key}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    for key in test_details.keys():
        assert test_details[key] == data[key]

@pytest.fixture
def contact_fields():
    contact_fields = [field.attname for field in Contact._meta.fields if field.attname not in ("id", "user_id")]
    return  contact_fields

@pytest.mark.django_db
def test_user_add_contact(test_user_active, authorized_client, contact_fields):
    # Arrange
    test_contact = baker.prepare(Contact, _fill_optional=True)
    # test_contact = contact_factory(_quantity=1, user_id=test_user_active.id)[0]

    # contact_fields = ( 'city', 'street', 'house', 'structure', 'building', 'apartment', 'phone')

    #contact_fields = [field.attname for field in Contact._meta.fields if field.attname not in ("id", "user_id")]

    # test_data = {
    #     "city":test_contact.city,
    #     "street":test_contact.street,
    #     "phone":test_contact.phone}

    test_data = {field: getattr(test_contact, field) for field in contact_fields}

    # Act
    response = authorized_client.post(reverse("my_app:user-contact"), follow=True,
                                      content_type="application/json", data=json.dumps(test_data))
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data.get("Status") is True
    test_user_active.refresh_from_db()
    contact = test_user_active.contacts.all()[0]
    # contacts = test_user_active.contacts.all()
    # contact = contacts.latest("id")
    for key in test_data.keys():
        assert test_data[key] == getattr(contact, key)


@pytest.fixture
def contact_factory():
    def factory(*args, **kwargs):
        return baker.make(Contact, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_user_get_contact(test_user_active, authorized_client, contact_factory, contact_fields):
    #Arrange
    test_contacts = contact_factory(_quantity=10, user_id=test_user_active.id, _fill_optional=True)

    #Act
    response = authorized_client.get(reverse("my_app:user-contact"), follow=True,
                                      content_type="application/json",)
    data = response.json()

    # Assert


    assert response.status_code == 200
    for i, response_contact in enumerate(data):
        for field in contact_fields:
            assert response_contact[field] == getattr(test_contacts[i], field)

