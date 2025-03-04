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
from tests.constants.product import (
    ANONYMOUS_CANT_CREATE_PRODUCT,
    ANONYMOUS_CANT_DELETE_PRODUCT,
    ANONYMOUS_CANT_EDIT_PRODUCT,
    EXPECTED_PRODUCTS_COUNT,
    NOT_ENOUGH_FIELDS,
    SUPERUSER_CAN_CREATE_PRODUCT,
    SUPERUSER_CAN_DELETE_PRODUCT,
    SUPERUSER_CAN_EDIT_PRODUCT,
    URL_PRODUCTS,
    USER_CANT_CREATE_PRODUCT,
    USER_CANT_DELETE_PRODUCT,
    USER_CANT_EDIT_PRODUCT,
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
    """Класс для тестирования Product"""

    def setUp(self):
        super().setUp()

        self.product = ProductFactory()

        self.url_products = URL_PRODUCTS
        self.url_products_create = URL_PRODUCTS
        self.url_products_edit = f'{URL_PRODUCTS}{self.product.id}'
        self.url_products_delete = f'{URL_PRODUCTS}{self.product.id}'

    def check_fields(self, data, required_fields, path=''):
        """
        Рекурсивная функция "unittest" для проверки наличия необходимых полей
        в ответе API с локального сервера. Работает с
        dict/list/tuple последовательностями, а так же вложенными.

            На вход принимает 3 аргумента:

                1. Аргумент "data":
                    json-словарь из "response.data".

                2. Аргумент required_fields:
                    последовательность ожидаемых в ответе полей.

                3. Аргумент "path":
                    указывает начальную глубину для прохода
                    по последовательностям, по дефолту = ''.

        """
        if isinstance(required_fields, dict):
            for field, expected_type in required_fields.items():
                field_path = f'{path}.{field}' if path else field
                self.assertIn(
                    field, data, NOT_ENOUGH_FIELDS.format(f'"{field}"')
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
        """Тест на существование эндпоинта для Products"""
        self._login(superuser=True)
        response = self.client.get(self.url_products)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f'Проверьте что определен эндпоинт {self.url_products}',
        )

    def test_create_product(self):
        """Тест создания продукта."""

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

        #  Проверка доступности эндпоинта для юзеров с разными правами.
        #  Anonymous User.
        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.OK,
            ANONYMOUS_CANT_CREATE_PRODUCT,
        )

        #  Authenticated User.
        self._login()
        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.OK,
            USER_CANT_CREATE_PRODUCT,
        )

        #  Superuser - создание Product.
        self._login(superuser=True)
        response = self.client.post(
            self.url_products_create, data=data, format='json'
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.CREATED,
            SUPERUSER_CAN_CREATE_PRODUCT,
        )

        #  Проверка на количесто объектов в БД после создания.
        products_count = Product.objects.count()
        self.assertEqual(
            products_count,
            EXPECTED_PRODUCTS_COUNT,
            'Убедитесь что Product был создан.',
        )

        #  Проверка наличия необходимых ключей в ответе.
        self.check_fields(response.data, REQUIRED_FIELDS)

        #  Проверка что созданные данные являются исходными.
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['description'], data['description'])
        self.assertEqual(response.data['price'], data['price'])
