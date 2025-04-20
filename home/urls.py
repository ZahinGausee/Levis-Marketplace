from django.urls import path , include
from home.views import index, about_us, contact_us

urlpatterns = [
    path('', index, name='index'),
    path('about/', about_us, name='about-us'),
    path("contact/", contact_us, name="contact-us")
] 
