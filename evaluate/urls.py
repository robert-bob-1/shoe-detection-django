from django.urls import path

from . import views

urlpatterns = [
    path('scrape/', views.process_product_from_url, name='scrape')
]