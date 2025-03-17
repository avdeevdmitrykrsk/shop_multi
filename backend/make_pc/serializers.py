# Thirdparty imports
from rest_framework import serializers

# Projects imports
from make_pc.models import PcDIY
from products.models import Product
from products.serializers import GetProductSerializer


class GetPcDIYSerializer(serializers.ModelSerializer):
    RELATED_FIELDS_MAPPING = {
        'pc_box': 'PC_BOX',
        'power_supply': 'POWER_SUPPLY',
        'motherboard': 'MOTHERBOARD',
        'ram_memory': 'RAM',
        'ssd_storage_memory': 'SSD',
        'hdd_storage_memory': 'HDD',
        'cpu': 'CPU',
        'gpu': 'GPU',
    }
    err_mes = 'ожидается объект с product_type == {}, вы пытаетесь добавить {}'

    class Meta:
        model = PcDIY
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.RELATED_FIELDS_MAPPING:
            self.fields[field_name] = GetProductSerializer()


class PcDIYSerializer(GetPcDIYSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.RELATED_FIELDS_MAPPING:
            self.fields[field_name] = serializers.PrimaryKeyRelatedField(
                queryset=Product.objects.all()
            )

    def validate(self, attrs):
        for field, obj in attrs.items():
            if (
                product_type := obj.product_type.name
            ) != self.RELATED_FIELDS_MAPPING[field]:
                raise serializers.ValidationError(
                    {
                        field: (
                            self.err_mes.format(
                                self.RELATED_FIELDS_MAPPING[field],
                                product_type,
                            )
                        )
                    }
                )

        return super().validate(attrs)

    def to_representation(self, instance):
        return GetPcDIYSerializer(instance).data
