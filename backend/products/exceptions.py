from rest_framework.exceptions import APIException


class ProductAlreadyExist(APIException):
    status_code = 400
    default_detail = 'Вы уже оценили этот продукт.'
    default_code = 'product_already_rated'
