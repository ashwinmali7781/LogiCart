from django.contrib import admin
from .models import Product, Contact, Orders, OrderUpdate, Review, Coupon, Wishlist, Newsletter, ReturnRequest


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'subcategory', 'price', 'original_price', 'stock', 'is_featured', 'is_active', 'pub_date')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('product_name', 'desc')
    list_editable = ('is_featured', 'is_active', 'stock')
    ordering = ('-pub_date',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_read', 'submitted_at')
    list_filter = ('is_read',)
    list_editable = ('is_read',)
    search_fields = ('name', 'email')
    readonly_fields = ('submitted_at',)


class OrderUpdateInline(admin.TabularInline):
    model = OrderUpdate
    extra = 1
    readonly_fields = ('timestamp',)


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'email', 'amount', 'discount_amount', 'status', 'city', 'created_at')
    list_filter = ('status', 'state')
    search_fields = ('name', 'email', 'order_id')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    inlines = [OrderUpdateInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')
    list_editable = ('is_approved',)
    search_fields = ('name', 'email', 'product__product_name')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'used_count', 'max_uses', 'valid_from', 'valid_to', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('email',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('product', 'session_key', 'added_at')
    search_fields = ('product__product_name',)


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason')
    list_editable = ('status',)
    search_fields = ('order__name', 'order__email')
    readonly_fields = ('created_at', 'updated_at')
