# Thirdparty imports
from django.core.cache import cache
from django.db import models

# Projects imports
from products.models import Product, ProductProperty


class PcDIYManager(models.Manager):

    def get_annotated_queryset(self, user):
        product_property_queryset = cache.get('product_property_queryset')
        if not product_property_queryset:
            product_property_queryset = ProductProperty.objects.select_related(
                'property'
            )
            cache.set(
                'product_property_queryset', product_property_queryset, 10
            )

        queryset = super().get_queryset()

        return queryset.select_related(
            'pc_box__creator',
            'pc_box__category',
            'pc_box__sub_category',
            'pc_box__article_by_product',
            'pc_box__product_type',
            'power_supply__creator',
            'power_supply__category',
            'power_supply__sub_category',
            'power_supply__article_by_product',
            'power_supply__product_type',
            'motherboard__creator',
            'motherboard__category',
            'motherboard__sub_category',
            'motherboard__article_by_product',
            'motherboard__product_type',
            'ram_memory__creator',
            'ram_memory__category',
            'ram_memory__sub_category',
            'ram_memory__article_by_product',
            'ram_memory__product_type',
            'ssd_storage_memory__creator',
            'ssd_storage_memory__category',
            'ssd_storage_memory__sub_category',
            'ssd_storage_memory__article_by_product',
            'ssd_storage_memory__product_type',
            'hdd_storage_memory__creator',
            'hdd_storage_memory__category',
            'hdd_storage_memory__sub_category',
            'hdd_storage_memory__article_by_product',
            'hdd_storage_memory__product_type',
            'cpu__creator',
            'cpu__category',
            'cpu__sub_category',
            'cpu__article_by_product',
            'cpu__product_type',
            'gpu__creator',
            'gpu__category',
            'gpu__sub_category',
            'gpu__article_by_product',
            'gpu__product_type',
        ).prefetch_related(
            models.Prefetch(
                'pc_box__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'power_supply__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'motherboard__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'ram_memory__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'ssd_storage_memory__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'hdd_storage_memory__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'cpu__product_property_prod',
                queryset=product_property_queryset,
            ),
            models.Prefetch(
                'gpu__product_property_prod',
                queryset=product_property_queryset,
            ),
        )


class PcDIY(models.Model):

    pc_box = models.ForeignKey(
        Product,
        verbose_name='Корпус',
        related_name='pc_box_by_product',
        on_delete=models.CASCADE,
    )
    power_supply = models.ForeignKey(
        Product,
        verbose_name='Блок питания',
        related_name='power_supply_by_product',
        on_delete=models.CASCADE,
    )
    motherboard = models.ForeignKey(
        Product,
        verbose_name='Материнская плата',
        related_name='motherboard_by_product',
        on_delete=models.CASCADE,
    )
    ram_memory = models.ForeignKey(
        Product,
        verbose_name='Оперативная память',
        related_name='ram_by_product',
        on_delete=models.CASCADE,
    )
    ssd_storage_memory = models.ForeignKey(
        Product,
        verbose_name='SSD накопитель',
        related_name='ssd_by_product',
        on_delete=models.CASCADE,
    )
    hdd_storage_memory = models.ForeignKey(
        Product,
        verbose_name='HDD накопитель',
        related_name='hdd_by_product',
        on_delete=models.CASCADE,
    )
    cpu = models.ForeignKey(
        Product,
        verbose_name='Процессор',
        related_name='cpu_by_product',
        on_delete=models.CASCADE,
    )
    gpu = models.ForeignKey(
        Product,
        verbose_name='Видеокарта',
        related_name='gpu_by_product',
        on_delete=models.CASCADE,
    )

    objects = PcDIYManager()

    class Meta:
        verbose_name = ('ПК сборка',)
        verbose_name_plural = ('ПК сборки',)
