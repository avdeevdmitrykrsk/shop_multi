from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if sender.name == 'users':
        User = get_user_model()
        if not User.objects.filter(email='edu-avdeev@ya.ru').exists():
            User.objects.create_superuser(
                username='homie',
                email='edu-avdeev@ya.ru',
                password='Zb0dd445'
            )
