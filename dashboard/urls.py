from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard_home'),
    # Products
    path('products/', views.product_list, name='dashboard_products'),
    path('products/add/', views.product_add, name='dashboard_product_add'),
    path('products/<int:pk>/edit/', views.product_edit, name='dashboard_product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='dashboard_product_delete'),
    # Orders
    path('orders/', views.order_list, name='dashboard_orders'),
    path('orders/<int:pk>/', views.order_detail, name='dashboard_order_detail'),
    path('orders/export/', views.orders_export_csv, name='dashboard_orders_export'),
    # Reviews
    path('reviews/', views.review_list, name='dashboard_reviews'),
    path('reviews/<int:pk>/action/', views.review_action, name='dashboard_review_action'),
    # Messages
    path('messages/', views.message_list, name='dashboard_messages'),
    path('messages/<int:pk>/', views.message_detail, name='dashboard_message_detail'),
    # Coupons
    path('coupons/', views.coupon_list, name='dashboard_coupons'),
    path('coupons/add/', views.coupon_add, name='dashboard_coupon_add'),
    path('coupons/<int:pk>/delete/', views.coupon_delete, name='dashboard_coupon_delete'),
    # Newsletter
    path('newsletter/', views.newsletter_list, name='dashboard_newsletter'),
    path('newsletter/export/', views.newsletter_export, name='dashboard_newsletter_export'),
    # Return Requests
    path('returns/', views.return_list, name='dashboard_returns'),
    path('returns/<int:pk>/action/', views.return_action, name='dashboard_return_action'),
]
