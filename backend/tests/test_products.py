# Standart lib imports
import json
from http import HTTPStatus
from pprint import pprint

# Thirdparty imports
from django.contrib.auth import get_user_model
from django.urls import reverse
from dotmap import DotMap
from rest_framework.test import APITestCase

# Projects imports
from products.models import Product, ProductProperty, Property
from tests.constants.product import (
    ANONYMOUS_CANT_CREATE_PRODUCT,
    ANONYMOUS_CANT_DELETE_PRODUCT,
    ANONYMOUS_CANT_EDIT_PRODUCT,
    ENDPOINT_EXIST,
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
        """Аутентификация по токену."""
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

    def check_access_by_different_users(self, url, choose_method=None):
        """Проверка доступности эндпоинта для юзеров с разными правами."""

        http_methods = DotMap(
            post=self.client.post,
            patch=self.client.patch,
            delete=self.client.delete,
        )

        if (
            not choose_method
            or not isinstance(choose_method, str)
            or choose_method not in http_methods
        ):
            raise TypeError(
                'Параметр "choose_method" указан неверно, либо не указан.'
                ' Укажите метод "post/patch/delete".'
            )
        http_method = http_methods[choose_method]

        data_to_send = {
            "name": "test_produc1",
            "description": "test_description",
            "price": 1,
            "properties": [
                {"id": 1, "value": 3000},
                {"id": 2, "value": 50000},
            ],
        }

        pre_data = {
            '/api/v1/products/': {
                'post': {
                    'anonymous': {
                        'status': HTTPStatus.OK,
                        'message': ANONYMOUS_CANT_CREATE_PRODUCT,
                    },
                    'authenticated': {
                        'status': HTTPStatus.OK,
                        'message': USER_CANT_CREATE_PRODUCT,
                    },
                    'superuser': {
                        'status': HTTPStatus.CREATED,
                        'message': SUPERUSER_CAN_CREATE_PRODUCT,
                    },
                }
            },
            '/api/v1/products/1/': {
                'patch': {
                    'anonymous': {
                        'status': HTTPStatus.OK,
                        'message': ANONYMOUS_CANT_EDIT_PRODUCT,
                    },
                    'authenticated': {
                        'status': HTTPStatus.OK,
                        'message': USER_CANT_EDIT_PRODUCT,
                    },
                    'superuser': {
                        'status': HTTPStatus.OK,
                        'message': SUPERUSER_CAN_EDIT_PRODUCT,
                    },
                }
            },
        }
        assertion_data = DotMap(pre_data)

        #  Anonymous User.
        response = http_method(url, data=data_to_send, format='json')
        self.assertNotEqual(
            response.status_code,
            assertion_data[url][choose_method].anonymous.status,
            assertion_data[url][choose_method].anonymous.message,
        )

        #  Authenticated User.
        self._login()
        response = http_method(url, data=data_to_send, format='json')
        self.assertNotEqual(
            response.status_code,
            assertion_data[url][choose_method].authenticated.status,
            assertion_data[url][choose_method].authenticated.message,
        )

        #  Superuser - создание Product.
        self._login(superuser=True)
        response = http_method(url, data=data_to_send, format='json')
        self.assertEqual(
            response.status_code,
            assertion_data[url][choose_method].superuser.status,
            assertion_data[url][choose_method].superuser.message,
        )
        return response


class ProductTestCase(PreData, APITestCase):
    """Класс для тестирования Product"""

    def setUp(self):
        super().setUp()

        self.product = ProductFactory()

        self.url_products = URL_PRODUCTS
        self.url_products_create = URL_PRODUCTS
        self.url_products_edit = f'{URL_PRODUCTS}{self.product.id}/'
        self.url_products_delete = f'{URL_PRODUCTS}{self.product.id}/'

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

        elif isinstance(required_fields, (list, tuple)):
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

    def test_01_endpoint_exists(self):
        """Тест на существование эндпоинта для Products"""
        self._login(superuser=True)
        response = self.client.get(self.url_products)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            ENDPOINT_EXIST.format(self.url_products),
        )

    def test_02_create_product(self):
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
                    'name': str,
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

        response = self.check_access_by_different_users(
            self.url_products_create, choose_method='post'
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

    def test_03_edit_product(self):
        """Тест изменения продукта."""

        edited_data = {
            "name": "test_produc1",
            "description": "test_description",
            "price": 1,
            "properties": [
                {"id": 1, "value": 3000},
                {"id": 2, "value": 50000},
            ],
        }

        response = self.check_access_by_different_users(
            self.url_products_edit, choose_method='patch'
        )

        response = self.client.patch(
            self.url_products_edit, edited_data, format='json'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        #  Проверка что новые данные изменились.
        self.assertEqual(response.data['name'], edited_data['name'])
        self.assertEqual(
            response.data['description'], edited_data['description']
        )
        self.assertEqual(response.data['price'], edited_data['price'])
