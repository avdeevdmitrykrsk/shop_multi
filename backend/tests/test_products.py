# Standart lib imports
import json
from http import HTTPStatus

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


class ProductTestCase(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.superuser = SuperUserFactory()
        self.product = ProductFactory()

        self.url_create = reverse('products_v1-list')
        self.url_edit = reverse('products_v1-detail', args=[self.product.id])
        self.url_delete = reverse('products_v1-detail', args=[self.product.id])

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

        REQUIRED_FIELDS = (
            'name',
            'description',
            'price',
            'properties',
            'creator',
        )
        REQUIRED_PROPERTIES_FIELDS = ('id', 'value')

        response = self.client.post(self.url_create, data=data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

        self._login()
        response = self.client.post(self.url_create, data=data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

        self._login(superuser=True)
        response = self.client.post(self.url_create, data=data, format='json')
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        self.assertTrue(
            all(field in response.data for field in REQUIRED_FIELDS)
        )

        for property in response.data['properties']:
            for field in REQUIRED_PROPERTIES_FIELDS:
                self.assertIn(field, property)
