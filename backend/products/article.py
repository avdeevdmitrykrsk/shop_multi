from django.db.models import Max

from products.constants import DEFAULT_ARTICLE_DIGIT
from products.models import Article


class MakeUniqueArticle:

    def _get_prefix(self, instance):
        return (
            f'{instance.category.name[:3].upper()}-'
            f'{instance.sub_category.name[:3].upper()}'
        )


    def _get_unique_articl_digit(self):
        max_digit = (
            Article.objects.all()
            .values('article')
            .aggregate(Max('article'))['article__max']
        )

        if max_digit is not None:
            max_digit = int(max_digit.split(':')[-1])
            max_digit += 1
            return str(max_digit)

        return DEFAULT_ARTICLE_DIGIT

    def create(self, instance):
        prefix = self._get_prefix(instance)
        unique_digit = self._get_unique_articl_digit()
        article = f'{prefix}:{unique_digit}'

        Article.objects.create(product=instance, article=article)


article_util = MakeUniqueArticle()
