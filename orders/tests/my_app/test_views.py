import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
import json
from django.http import QueryDict

from my_app.models import ConfirmEmailToken, User
from requests_toolbelt.multipart.encoder import MultipartEncoder


def test_test():
    print(17)
    assert 2 == 2


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
        "email": "Test15@aaa.aa",
        "company": "TCompany",
        "password": "Q1W2E3aaa",
        "position": "Tposition"
    }

    data_multi = MultipartEncoder(
        fields=data)

    query_dict = QueryDict('', mutable=True)
    query_dict.update(data)
    json_data = json.dumps(query_dict)

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
