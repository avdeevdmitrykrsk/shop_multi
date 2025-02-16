# Thirdparty imports
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import RegexValidator
from django.db import models

# Projects imports
from users.constants import (USER_EMAIL_LENGTH, USER_FIRSTNAME_LENGTH,
                             USER_LASTNAME_LENGTH, USER_USERNAME_LENGTH)


class ShopUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class ShopUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name')

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Номер телефона',
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')],
    )
    username = models.CharField(
        unique=True,
        max_length=USER_USERNAME_LENGTH,
        verbose_name='username',
        validators=[UnicodeUsernameValidator()],
    )
    email = models.EmailField(
        unique=True, max_length=USER_EMAIL_LENGTH, verbose_name='email'
    )
    telegram_id = models.PositiveBigIntegerField(
        unique=True, verbose_name='Telegram ID', blank=True, null=True
    )
    first_name = models.CharField(
        max_length=USER_FIRSTNAME_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_LASTNAME_LENGTH, verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/images/', null=True, verbose_name='Аватар'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = ShopUserManager()

    class Meta:
        ordering = ('username',)
        verbose_name = ('Пользователь',)
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:15]
