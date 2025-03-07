# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Projects imports
from products.models import (
    Category,
    Product,
    ProductProperty,
    ProductSubCategory,
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
            user = User.objects.get(id=1)

            product = Product.objects.create(
                name='unittest_product',
                description="test_description",
                category=category,
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

            product_sub_categories = []
            sub_categories_data = (
                {
                    'name': 'ЖК',
                    'slug': 'televisors',
                },
                {
                    'name': 'Смартфоны',
                    'slug': 'Smartphones',
                },
            )

            for data in sub_categories_data:
                sub_category = SubCategory.objects.create(
                    name=data['name'],
                    slug=data['slug'],
                )
                product_sub_categories.append(
                    ProductSubCategory(
                        product=product, sub_category=sub_category
                    )
                )
            ProductSubCategory.objects.bulk_create(product_sub_categories)
