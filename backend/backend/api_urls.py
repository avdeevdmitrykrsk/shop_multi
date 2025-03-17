# Thirdparty imports
from django.urls import include, path

# V1
urlpatterns = [
    path('v1/', include('users.urls')),
    path('v1/', include('products.urls')),
    path('v1/', include('make_pc.urls')),
]
