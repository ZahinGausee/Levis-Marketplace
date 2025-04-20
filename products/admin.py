from django.contrib import admin
from .models import *

class ProductAdminImage(admin.StackedInline):
    model = ProductImage
    extra = 1  # Allows adding multiple images
    fields = ['image', 'color_variant']  # Enables color-specific images

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'RRP', 'stock_quantity', 'sub_category']
    inlines = [ProductAdminImage]

class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', 'is_expired', 'discount_price', 'minimum_amount']
    

@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ['color_name', 'price']

@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ['size_name', 'price']

admin.site.register(Product, ProductAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(Category)
admin.site.register(SubCategory)
