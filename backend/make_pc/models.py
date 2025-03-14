from django.db import models

from products.models import Product

class PcDIY(models.Model):

    pc_box = models.ForeignKey(
        Product,
        verbose_name='Корпус',
        related_name='pc_box_by_product',
        on_delete=models.CASCADE,
        unique=True,
    ),
    power_supply = models.ForeignKey(
        Product,
        verbose_name='Блок питания',
        related_name='power_supply_by_product',
        on_delete=models.CASCADE,
        unique=True,
    ),
    mothrboard = models.ForeignKey(
        Product,
        verbose_name='Материнская плата',
        related_name='motherboard_by_product',
        on_delete=models.CASCADE,
        unique=True,
    ),
    ram_memory = models.ForeignKey(
        Product,
        verbose_name='Оперативная память',
        related_name='ram_by_product',
        on_delete=models.CASCADE,
    ),
    ssd_storage_memory = models.ForeignKey(
        Product,
        verbose_name='SSD накопитель',
        related_name='ssd_by_product',
        on_delete=models.CASCADE,
    ),
    hdd_storage_memory = models.ForeignKey(
        Product,
        verbose_name='HDD накопитель',
        related_name='hdd_by_product',
        on_delete=models.CASCADE,
    ),
    cpu = models.ForeignKey(
        Product,
        verbose_name='Процессор',
        related_name='cpu_by_product',
        on_delete=models.CASCADE,
        unique=True,
    ),
    gpu = models.ForeignKey(
        Product,
        verbose_name='Видеокарта',
        related_name='gpu_by_product',
        on_delete=models.CASCADE,
        unique=True,
    ),

    class Meta:
        verbose_name = 'ПК сборка',
        verbose_name_plural = 'ПК сборки',
