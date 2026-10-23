from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Enquiry

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "active", "featured")
    list_filter = ("category", "active", "featured")
    search_fields = ("name", "brand")
    list_editable = ("price", "stock", "active", "featured")

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "size", "colour", "quantity", "unit_price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "email", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "email", "razorpay_order_id")
    list_editable = ("status",)
    inlines = [OrderItemInline]

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "subject", "created_at")
    search_fields = ("name", "email", "subject")
