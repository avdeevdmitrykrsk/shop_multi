# Standart lib imports
import json
from http import HTTPStatus
from pprint import pprint

# Thirdparty imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

# Projects imports
from products.models import Product, ProductProperty, Property
from tests.assert_messages.product import (
    ANONYMOUS_CANT_CREATE_EDIT_DELETE_PRODUCT,
    SUPERUSER_CAN_CREATE_EDIT_DELETE_PRODUCT,
)
from tests.factories import ProductFactory, SuperUserFactory, UserFactory

User = get_user_model()


class PreData:

    def setUp(self):
        self.user = UserFactory()
        self.superuser = SuperUserFactory()

    def _login(self, superuser=None):
        token_url = reverse('jwt-create')

        email = self.user.email
        if superuser:
            email = self.superuser.email
        password = 'Zb0dd445'

        response = self.client.post(
            token_url,
            {"email": email, "password": password},
        )
        token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')


class ProductTestCase(PreData, APITestCase):

    def setUp(self):
        super().setUp()

        self.product = ProductFactory()
        self.url_products = '/api/v1/products/'
        self.url_products_create = reverse('products_v1-list')
        self.url_products_edit = reverse(
            'products_v1-detail', args=[self.product.id]
        )
        self.url_products_delete = reverse(
            'products_v1-detail', args=[self.product.id]
        )

    def check_fields(self, data, required_fields, path=''):
        if isinstance(required_fields, dict):
            for field, expected_type in required_fields.items():
                field_path = f'{path}.{field}' if path else field
                self.assertIn(
                    field, data, f'Поле "{field_path}" отсутствует в ответе.'
                )
                self.check_fields(data[field], expected_type, field_path)

        elif isinstance(required_fields, (list or tuple)):
            for index, item in enumerate(data):
                item_path = f'{path}[{index}]'
                self.check_fields(item, required_fields[0], item_path)

        else:
            self.assertIsInstance(
                data,
                required_fields,
                (
                    f'Поле "{path}" имеет тип {type(data)},'
                    f' ожидается {required_fields}.',
                ),
            )

    def test_endpoint_exists(self):
        self._login(superuser=True)
        response = self.client.get(self.url_products)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Проверьте что определен эндпоинт {self.url_products}',
        )

    def test_create_product(self):
        data = {
            "name": "test_produc1",
            "description": "test_description",
            "price": 1,
            "properties": [
                {"id": 1, "value": 3000},
                {"id": 2, "value": 50000},
            ],
        }

        REQUIRED_FIELDS = {
            'id': int,
            'name': str,
            'description': str,
            'price': int,
            'properties': [
                {
                    'id': int,
                    'value': str,
                }
            ],
            'creator': {
                'id': int,
                'username': str,
                'first_name': str,
                'last_name': str,
                'email': str,
                'phone_number': str,
            },
            'rating': int,
            'article': int,
            'created_at': str,
            'updated_at': str,
        }

        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self._login()
        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self._login(superuser=True)
        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        pprint(response.data['article'])
        #  Проверка наличия необходимых ключей в ответе.
        self.check_fields(response.data, REQUIRED_FIELDS)
