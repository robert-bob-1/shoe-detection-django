from django.urls import path

from . import views

urlpatterns = [
    path('get-all/', views.get_all, name='get_all'),
    path('get-images/', views.get_images, name='get_images')
]