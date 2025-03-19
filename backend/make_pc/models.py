# Thirdparty imports
from django.db import models

# Projects imports
from make_pc.constants import PC_DIY_QUERY_STMNT
from products.models import Product, ProductProperty


class PcDIYManager(models.Manager):

    def get_annotated_queryset(self, user):
        product_property_queryset = ProductProperty.objects.select_related(
            'property'
        )

        prefetch_fields = [
            'pc_box',
            'power_supply',
            'motherboard',
            'ram_memory',
            'ssd_storage_memory',
            'hdd_storage_memory',
            'cpu',
            'gpu',
        ]

        prefetches = [
            models.Prefetch(
                f'{field}__product_property_prod',
                queryset=product_property_queryset,
            )
            for field in prefetch_fields
        ]

        queryset = super().get_queryset()

        return queryset.select_related(*PC_DIY_QUERY_STMNT).prefetch_related(
            *prefetches
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
