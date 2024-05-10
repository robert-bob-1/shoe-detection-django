from django.urls import path

from . import views

urlpatterns = [
    path('scrape_photos/', views.process_product_from_url, name='scrape')
]