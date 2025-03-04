# # Thirdparty imports
# import pytest
# from fixtures.user import (  # noqa F401
#     client_superuser,
#     client_anonymous,
#     client_staff,
#     client_user,
#     user_create_data,
#     user_create_data_2,
#     users_me_url,
#     users_url,
# )
# from rest_framework import status
# from rest_framework.test import APIClient


# class PermissionError(Exception):

#     def __init__(self, message, status_code=401):
#         self.message = message
#         self.status_code = status_code

#     def __str__(self):
#         return self.message


# @pytest.mark.django_db
# class TestUsers:

#     def test_user_create(
#         self,
#         users_url,
#         client_anonymous: APIClient,
#         client_user: APIClient,
#         client_staff: APIClient,
#         client_superuser: APIClient,
#         user_create_data: dict,
#         user_create_data_2,
#     ):

#         # for client in (client_user, client_staff):
#         response = client_user.post(users_url, user_create_data)
#         assert response.status_code == status.HTTP_201_CREATED
#         response = client_staff.post(users_url, user_create_data_2)
#         assert response.status_code == status.HTTP_201_CREATED

#         # response = client_anonymous.post(users_url, user_create_data)
#         # assert response.status_code == status.HTTP_201_CREATED

#     @pytest.mark.django_db
#     def test_users_me_endpoint(
#         self,
#         users_me_url,
#         client_anonymous: APIClient,
#         client_user: APIClient,
#     ):
#         try:
#             response = client_anonymous.get(users_me_url)
#             assert response.status_code == status.HTTP_401_UNAUTHORIZED
#         except Exception:
#             raise PermissionError(
#                 'Неаутентифицированный пользователь не должен иметь'
#                 f' доступ к данному эндпоинту - {users_me_url}'
#             )

#         response = client_user.get(users_me_url)
#         assert response.status_code == status.HTTP_200_OK
