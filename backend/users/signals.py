# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if sender.name == 'users':
        User.objects.create_superuser(
            username='homie',
            email='edu-avdeev@ya.ru',
            password='Zb0dd445',
            phone_number=9232982225,
        )
        User.objects.create_user(
            username='homie_just_a_user',
            email='user@ya.ru',
            password='Zb0dd445',
            phone_number=9232982226,
        )
