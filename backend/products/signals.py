# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Projects imports
from products.models import (
    Category,
    Product,
    ProductProperty,
    Property,
    SubCategory,
)

User = get_user_model()


@receiver(post_migrate)
def create_product(sender, **kwargs):
    if sender.name == 'products':
        if not Product.objects.filter(name='unittest_product').exists():
            category = Category.objects.create(
                name='Телефоны',
                slug='smartphones',
            )
            sub_category = SubCategory.objects.create(
                name='Водонепроницаемые',
                slug='waterdefence',
            )
            user = User.objects.get(id=1)

            product = Product.objects.create(
                name='unittest_product',
                description="test_description",
                category=category,
                sub_category=sub_category,
                price=1000,
                creator=user,
            )

            product_properties = []
            property_data = (
                {'value': 30000, 'name': 'Ёмкость АКБ'},
                {'value': 8, 'name': 'Ширина'},
                {'value': 19, 'name': 'Длина'},
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
