from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Cart URLs
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:cart_item_id>/', views.update_cart, name='update_cart'),  # Keep for backward compatibility
    
    # New plus/minus quantity controls
    path('cart/increase/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    
    # Optional AJAX URLs for better UX
    path('cart/ajax/increase/<int:cart_item_id>/', views.ajax_increase_quantity, name='ajax_increase_quantity'),
    path('cart/ajax/decrease/<int:cart_item_id>/', views.ajax_decrease_quantity, name='ajax_decrease_quantity'),
    
    # Wishlist URLs
    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),

    path('about/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
]