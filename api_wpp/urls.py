from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.create_product, name='create_product'),
    path('products/<int:pk>/', views.update_product, name='update_product'),
    path('products/<int:pk>/', views.delete_product, name='delete_product'),
    path('process_sale/', views.process_sale, name='process_sale'),
    path('customer/<uuid:customer_id>/', views.customer_page, name='customer_page'),
]
