from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.create_product, name='create_product'),
    path('products/<int:pk>/', views.update_product, name='update_product'),
    path('products/<int:pk>/', views.delete_product, name='delete_product'),
    path('process_sale/', views.process_sale, name='process_sale'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/connect/', views.connect_instance, name='connect_instance'),
    path('customer/<uuid:customer_id>/', views.customer_page, name='customer_page'),
    path('customer/refresh/', views.refresh_code, name='refresh_code'),
]
