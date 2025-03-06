# Thirdparty imports
from django.contrib.auth import get_user_model
from django.db import models

# Projects imports
from .constants import (
    DEFAULT_RATING,
    LONG_STR_CUT_VALUE,
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    MAX_VALUE_LENGTH,
)

User = get_user_model()


class Property(models.Model):

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Характеристика',
        unique=True,
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'

    def __str__(self):
        return self.name


class ProductManager(models.Manager):

    def get_annotated_queryset(self, user):
        queryset = super().get_queryset()
        return queryset.annotate(
            is_favorited=models.Exists(
                Favorite.objects.filter(
                    user=user, product=models.OuterRef('pk')
                )
            ),
            is_in_shopping_cart=models.Exists(
                ShoppingCart.objects.filter(
                    user=user, product=models.OuterRef('pk')
                )
            ),
        ).order_by('name', 'creator')


class Product(models.Model):
    """Модель Продукта"""

    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование',
        unique=True,
        blank=False,
        help_text=(
            'Максимально допустимое число знаков - ',
            f'{MAX_NAME_LENGTH}.',
        ),
    )
    description = models.TextField(
        max_length=MAX_DESCRIPTION_LENGTH,
        verbose_name='Описание',
        blank=False,
        help_text=(
            'Максимально допустимое число знаков - ',
            f'{MAX_DESCRIPTION_LENGTH}.',
        ),
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена', help_text='Укажите цену', blank=False
    )
    properties = models.ManyToManyField(
        to=Property,
        through='ProductProperty',
        verbose_name='Характеристики',
        related_name='product_by_property',
    )
    creator = models.ForeignKey(
        User,
        verbose_name='Создатель',
        on_delete=models.CASCADE,
        null=False,
    )
    article = models.PositiveBigIntegerField(
        verbose_name='Артикул', blank=False, null=False, unique=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания', blank=False, auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления', blank=True, auto_now=True
    )

    objects = ProductManager()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def save(self, *args, **kwargs):
        if not self.article:
            max_article = Product.objects.aggregate(models.Max('article'))[
                'article__max'
            ]
            self.article = max_article + 1 if max_article is not None else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductProperty(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_property_prod'
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='product_property_prop',
    )
    value = models.CharField(
        max_length=MAX_VALUE_LENGTH,
        verbose_name='Значение характеристики',
        blank=False,
        null=False,
    )

    class Meta:
        unique_together = ('product', 'property')
        verbose_name = 'Характеристика продукта'
        verbose_name_plural = 'Характеристики продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'property'), name='unique_product_property'
            )
        ]

    def __str__(self):
        return f'{self.product.name}: {self.property.name} - {self.value}'


class RatingFavoriteShoppingCart(models.Model):
    """Абстрактная модель для Rating/Favorite/ShoppingCart"""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('user', 'product')

    def __str__(self):
        return f'{self.user} has a {self.recipe[:LONG_STR_CUT_VALUE]}.'


class Rating(RatingFavoriteShoppingCart):

    score = models.PositiveSmallIntegerField(
        verbose_name='Счет', blank=False, null=False
    )

    class Meta(RatingFavoriteShoppingCart.Meta):
        default_related_name = 'rating_list'
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'product'), name='unique_rating_user_product'
            )
        ]


class Favorite(RatingFavoriteShoppingCart):

    class Meta(RatingFavoriteShoppingCart.Meta):
        default_related_name = 'favorite_list'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'product'), name='unique_favorite_user_product'
            )
        ]


class ShoppingCart(RatingFavoriteShoppingCart):

    class Meta(RatingFavoriteShoppingCart.Meta):
        default_related_name = 'shopping_cart_list'
        verbose_name = 'Добавлен в корзину'
        verbose_name_plural = 'Добавлены в корзину'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'product'),
                name='unique_shopping_cart_user_product',
            )
        ]
