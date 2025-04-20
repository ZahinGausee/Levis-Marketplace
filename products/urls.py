from django.urls import path
from products.views import get_product, shop

urlpatterns = [
    path('shop/', shop, name="shop"),
    path('<slug>/' , get_product , name="get_product"),
]
