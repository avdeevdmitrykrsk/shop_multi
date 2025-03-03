# Thirdparty imports
import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

# Projects imports
from products.models import Product, Property

# from faker import Faker


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):

    email = factory.Faker('email')
    username = factory.LazyAttribute(lambda obj: obj.email)
    phone_number = factory.Faker('phone_number')
    password = factory.LazyFunction(lambda: make_password('Zb0dd445'))

    class Meta:
        model = User


class SuperUserFactory(UserFactory):

    is_staff = True
    is_superuser = True


class PropertyFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('word')

    class Meta:
        model = Property


class ProductFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('word')
    description = ("test_description_edited",)
    price = factory.Faker('random_int', min=1, max=1000)
    properties = factory.RelatedFactoryList(PropertyFactory, size=2)
    creator = factory.SubFactory(SuperUserFactory)

    class Meta:
        model = Product
