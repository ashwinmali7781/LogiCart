from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='ShopHome'),
    path('about/', views.about, name='AboutUs'),
    path('contact/', views.contact, name='ContactUs'),
    path('tracker/', views.tracker, name='TrackOrder'),
    path('search/', views.search, name='Search'),
    path('products/<int:myid>/', views.productView, name='ProductView'),
    path('checkout/', views.checkout, name='CheckOut'),
    path('handlerequest/', views.handlerequest, name='HandleRequest'),
    # Wishlist
    path('wishlist/', views.wishlist_view, name='WishList'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='ToggleWishlist'),
    # Coupon
    path('coupon/apply/', views.apply_coupon, name='ApplyCoupon'),
    # Newsletter
    path('newsletter/subscribe/', views.newsletter_subscribe, name='NewsletterSubscribe'),
    # Returns
    path('returns/', views.request_return, name='ReturnRequest'),
    # Compare
    path('compare/', views.compare_products, name='CompareProducts'),
]
