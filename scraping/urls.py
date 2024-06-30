from django.urls import path

from . import views

urlpatterns = [
    path('scrape-product/', views.scrape_product, name='scrape_product'),
    path('scrape-page/', views.scrape_page, name='scrape_page'),
    path('website-update/', views.website_update, name='website_update'),
]