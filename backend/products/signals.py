# Thirdparty imports
import faker
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Projects imports
from products.constants import DEFAULT_ARTICLE_DIGIT
from products.models import (
    Article,
    Category,
    Product,
    ProductProperty,
    ProductType,
    Property,
    SubCategory,
)

User = get_user_model()

product_type_names = (
    'PC_BOX',
    'MOTHERBOARD',
    'POWER_SUPPLY',
    'RAM',
    'SSD',
    'HDD',
    'CPU',
    'GPU',
)


@receiver(post_migrate)
def create_category_sub_category(sender, **kwargs):

    if sender.name == 'products':

        Category.objects.create(
            name='Персональный компьютер',
            slug='personal computer',
        )
        SubCategory.objects.create(
            name='Комплектующие для ПК',
            slug='PC components',
        )

        data = []
        for product_type_name in product_type_names:
            data.append(ProductType(name=product_type_name))
        ProductType.objects.bulk_create(data)

        property_data = (
            {'value': 30000, 'name': 'Ёмкость АКБ'},
            {'value': 8, 'name': 'Ширина'},
            {'value': 19, 'name': 'Длина'},
        )

        data = []
        for property_name in property_data:
            data.append(Property(name=property_name['name']))
        Property.objects.bulk_create(data)


# @receiver(post_migrate)
# def create_product(sender, **kwargs):
#     if sender.name == 'products':

#         if not Product.objects.filter(name='unittest_product').exists():
#             property_data = (
#                 {'value': 30000, 'name': 'Ёмкость АКБ'},
#                 {'value': 8, 'name': 'Ширина'},
#                 {'value': 19, 'name': 'Длина'},
#             )

#             category = Category.objects.create(
#                 name='Телефоны',
#                 slug='smartphones',
#             )
#             sub_category = SubCategory.objects.create(
#                 name='Водонепроницаемые',
#                 slug='waterdefence',
#             )
#             user = User.objects.get(id=1)

#             for product_type_name in product_type_names:
#                 product_type = ProductType.objects.create(
#                     name=product_type_name
#                 )
#                 product = Product.objects.create(
#                     name=f'unittest_product - {product_type_name}',
#                     description="test_description",
#                     category=category,
#                     sub_category=sub_category,
#                     price=1000,
#                     creator=user,
#                     product_type=product_type,
#                 )

#                 product_properties = []

#                 property = Property.objects.create(name=product.name[:5])

#                 products = Product.objects.all()
#                 for product in products:
#                     product_properties.append(
#                         ProductProperty(
#                             product=product,
#                             property=property,
#                             value=faker.Faker().name,
#                         )
#                     )
#             ProductProperty.objects.bulk_create(product_properties)

#             products = Product.objects.all()
#             for item in products:
#                 article = str(int(DEFAULT_ARTICLE_DIGIT) + item.id)
#                 print(item)
#                 print(article)
#                 Article.objects.create(
#                     product=item, article=article
#                 )
