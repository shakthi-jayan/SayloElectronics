from django.contrib import admin
from .models import Product, Category, Cart, Wishlist

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Wishlist)
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]