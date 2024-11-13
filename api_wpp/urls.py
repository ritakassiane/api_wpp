from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.create_product, name='create_product'),
    path('products/<int:pk>/', views.update_product, name='update_product'),
    path('products/<int:pk>/', views.delete_product, name='delete_product'),
]
