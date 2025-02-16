from django.db import models


class Product(models.Model):

    name = models.CharField(
        max_length=255,
        verbose_name='Наименование',
        unique=True,
        blank=False,
        help_text=(
            'Максимально допустимое число знаков - ',
            f'{255}.'
        )
    )
    description = models.TextField(
        max_length=1000,
        verbose_name='Описание',
        blank=False,
        help_text=(
            'Максимально допустимое число знаков - ',
            f'{1000}.'
        )
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена',
        help_text='Укажите цену',
        blank=False
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        blank=False,
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        blank=True,
        auto_now=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
