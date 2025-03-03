# Standart lib imports
import json
from http import HTTPStatus

# Thirdparty imports
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

# Projects imports
from products.models import Product, ProductProperty, Property
from tests.assert_messages.product import (
    ANONYMOUS_CANT_CREATE_EDIT_DELETE_PRODUCT,
    SUPERUSER_CAN_CREATE_EDIT_DELETE_PRODUCT,
)

User = get_user_model()


# PRODUCT_DATA = {
#     "name": "test_produc1",
#     "description": "test_description",
#     "price": 1,
#     "properties": [{"id": 1, "value": 3000}, {"id": 2, "value": 50000}],
# }
# EDITED_PRODUCT_DATA = {
#     "name": "test_produc_edited",
#     "description": "test_description_edited",
#     "price": 10,
#     "properties": [{"id": 1, "value": 30000}, {"id": 2, "value": 500000}],
# }


class PreData(TestCase):
    """Необходимые данные для тестов"""

    @classmethod
    def setUpTestData(cls):
        cls.client_superuser = APIClient()
        cls.product = cls.create_product()
        cls.create_property()

        cls.client_superuser.credentials(
            HTTP_AUTHORIZATION='Bearer ' + cls.get_access_token()
        )

    def create_property():
        for name in range(1, 3):
            Property.objects.create(name=f'test_{name}')

    def create_product():
        user = User.objects.get(id=1)

        product = Product.objects.create(
            name='unittest_product',
            description="test_description",
            price=1,
            creator=user,
        )

        product_properties = []
        property_data = (
            {'value': 3000, 'name': 'prop1'},
            {'value': 50000, 'name': 'prop2'},
        )

        for data in property_data:
            property = Property.objects.create(name=data['name'])
            product_properties.append(
                ProductProperty(
                    product=product,
                    property=property,
                    value=data['value'],
                )
            )

        ProductProperty.objects.bulk_create(product_properties)
        return product

    @classmethod
    def get_access_token(cls):
        response = cls.client_superuser.post(
            reverse('jwt-create'),
            {'email': 'edu-avdeev@ya.ru', 'password': 'Zb0dd445'},
        )
        return response.data['access']


class TestProduct(PreData):
    """Тесты Product"""

    def setUp(self):
        super().setUp()
        self.data = (
            # (
            #     self.client,
            #     HTTPStatus.UNAUTHORIZED,
            #     ANONYMOUS_CANT_CREATE_EDIT_DELETE_PRODUCT,
            # ),
            (
                self.client_superuser,
                HTTPStatus.OK,
                SUPERUSER_CAN_CREATE_EDIT_DELETE_PRODUCT,
            ),
        )
        self.url_create = reverse('products_v1-list')
        self.url_edit = reverse('products_v1-detail', args=[self.product.id])
        self.url_delete = reverse('products_v1-detail', args=[self.product.id])

    def test_anonymous_user_cant_create_edit_delete_product(self):
        for client, status, message in self.data:
            # response = client.post(
            #     self.url_create,
            #     data=json.dumps(PRODUCT_DATA),
            #     content_type='application/json',
            # )
            # self.assertEqual(
            #     response.status_code,
            #     status,
            #     message,
            # )

            response = client.patch(
                self.url_edit,
                data=json.dumps(EDITED_PRODUCT_DATA),
                content_type='application/json',
            )
            self.assertEqual(
                response.status_code,
                status,
                message,
            )

            data = dict(response.data)
            properties = [dict(prop) for prop in data.get('properties')]
            for property in properties:
                property['id'] = int(property['id'])
                property['value'] = int(property['value'])

            data_to_check = {
                'name': data.get('name'),
                'description': data.get('description'),
                'price': data.get('price'),
                'properties': properties,
            }

            self.assertEqual(
                data_to_check,
                EDITED_PRODUCT_DATA,
                (
                    'Убедитесь что после patch-запроса '
                    'данные объекта были изменены.',
                ),
            )

            # response = client.delete(self.url_delete)
            # self.assertEqual(
            #     response.status_code,
            #     status,
            #     message,
            # )

        # def test_user_cant_create_edit_delete_product(self):
        #     response = self.client.post(
        #         self.url,
        #         data=json.dumps(PRODUCT_DATA),
        #         content_type='application/json',
        #     )
        #     self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)
