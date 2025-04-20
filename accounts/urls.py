from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import login_page, register_page, activate_email, user_logout, add_to_cart, cart, remove_cart, remove_coupon, success, user_details, user_orders

urlpatterns = [
    path('login/', login_page, name='login'),
    path('register/', register_page, name='register'),
    path("logout/", user_logout, name="logout"),
    path('activate/<email_token>/', activate_email, name='activate'),
    path('cart/', cart, name='cart'),
    path('add-to-cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove-cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('remove-coupon/<cart_id>/', remove_coupon, name='remove_coupon'),
    path('success/', success, name='success'),
    path('user-details/', user_details, name='user_details'),
    path('user-orders/', user_orders, name='user_orders'),
]