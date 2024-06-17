from django.urls import path

from . import views

urlpatterns = [
    path('scrape-product/', views.scrape_product, name='scrape_product'),
    path('scrape-page/', views.scrape_page, name='scrape_page'),
    path('color-similarity/', views.evaluate_color, name='evaluate_color'),
    path('shoe-types/', views.evaluate_shoe_type, name='evaluate_shoe_type'),
]