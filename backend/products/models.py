# Thirdparty imports
from django.contrib.auth import get_user_model
from django.core.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models

# Projects imports
from .constants import (
    CATEGORY_NAME_MAX_LENGTH,
    CATEGORY_SLUG_MAX_LENGTH,
    LONG_STR_CUT_VALUE,
    MAX_DESCRIPTION_LENGTH,
    MAX_NAME_LENGTH,
    MAX_PRICE_VALUE,
    MAX_VALUE_LENGTH,
    MIN_NAME_LENGTH,
    MIN_PRICE_VALUE,
)

User = get_user_model()


class SubCategory(models.Model):
    name = models.CharField(
        max_length=CATEGORY_NAME_MAX_LENGTH,
        verbose_name='Название',
        help_text=(
            'Максимально допустимое число знаков'
            f' - {CATEGORY_NAME_MAX_LENGTH}.'
        ),
        unique=True,
        db_index=True,
        null=False,
        blank=False,
    )
    slug = models.SlugField(
        max_length=CATEGORY_SLUG_MAX_LENGTH,
        verbose_name='Слаг',
        help_text=(
            'Максимально допустимое число знаков'
            f' - {CATEGORY_SLUG_MAX_LENGTH}.'
        ),
        unique=True,
        null=False,
        blank=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:LONG_STR_CUT_VALUE]


class Category(models.Model):
    name = models.CharField(
        max_length=CATEGORY_NAME_MAX_LENGTH,
        verbose_name='Название',
        help_text=(
            'Максимально допустимое число знаков'
            f' - {CATEGORY_NAME_MAX_LENGTH}.'
        ),
        unique=True,
        db_index=True,
        null=False,
        blank=False,
    )
    slug = models.SlugField(
        max_length=CATEGORY_SLUG_MAX_LENGTH,
        verbose_name='Слаг',
        help_text=(
            'Максимально допустимое число знаков'
            f' - {CATEGORY_SLUG_MAX_LENGTH}.'
        ),
        unique=True,
        db_index=True,
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Категория продукта'
        verbose_name_plural = 'Категории продуктов'

    def __str__(self):
        return f'{self.name}: {self.slug}'


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
        if user.is_authenticated:
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
        return queryset


class Product(models.Model):
    """Модель Продукта"""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products_by_category',
        blank=False,
        null=False,
    )
    sub_categories = models.ManyToManyField(
        to=SubCategory,
        through='ProductSubCategory',
        verbose_name='Подкатегория',
        related_name='products_by_sub_category',
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Наименование',
        unique=True,
        blank=False,
        db_index=True,
        help_text=(
            'Максимально допустимое число знаков - ',
            f'{MAX_NAME_LENGTH}.',
        ),
        validators=[
            MinLengthValidator(MIN_NAME_LENGTH),
        ],
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
        verbose_name='Цена',
        help_text='Укажите цену',
        blank=False,
        validators=[
            MinValueValidator(MIN_PRICE_VALUE),
            MaxValueValidator(MAX_PRICE_VALUE),
        ],
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
        return self.name[:LONG_STR_CUT_VALUE]


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
        verbose_name = 'Характеристика продукта'
        verbose_name_plural = 'Характеристики продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'property'), name='unique_product_property'
            )
        ]

    def __str__(self):
        return f'{self.product.name}: {self.property.name} - {self.value}'


class ProductSubCategory(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='product_sub_category_prod',
        null=False,
        blank=False,
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name='product_sub_category_cat',
        null=False,
        blank=False,
    )

    class Meta:
        verbose_name = 'Подкатегория продукта'
        verbose_name_plural = 'Подкатегории продуктов'
        constraints = [
            models.UniqueConstraint(
                fields=('product', 'sub_category'),
                name='unique_product_sub_category',
            )
        ]

    def __str__(self):
        return f'{self.product.name}: {self.sub_category.name}'


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
