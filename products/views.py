from pydoc import render_doc
from tkinter import E
from django.shortcuts import render
from products.models import Product, Category, SubCategory


def get_product(request , slug):
    try:

        product = Product.objects.get(slug = slug)
        ordered_images = product.product_images.all().order_by("uid")  # Fetch images in ascending order
        size_variants = product.size_variant.all().order_by("size_name")
        color_variants = product.color_variant.all().order_by("color_name")  # Get available colors


        default_size = request.GET.get("size") or (size_variants.first().size_name if size_variants.exists() else None)
        default_color = request.GET.get("color") or (color_variants.first().color_name if color_variants.exists() else None)

        discount_percentage = 0
        if product.RRP and product.price < product.RRP:
            discount_percentage = round(((product.RRP - product.price) / product.RRP) * 100)


        context = {
            "product": product,
            'ordered_images': ordered_images,
            "size_variants": size_variants,
            "color_variants": color_variants,
            "default_size": default_size,
            "default_color": default_color,
            "discount_percentage": discount_percentage,
        }
        
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_price_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price
            print('price',price)
        return render(request  , 'products/product.html' , context = context)

    except Exception as e:
        print(e)


def shop(request):

    categories = Category.objects.prefetch_related(
        'subcategories', 
        'subcategories__products', 
        'subcategories__products__product_images'
    ).all()
    for cat in Category.objects.all():
        print(f"Category: {cat.category_name}")
        for sub in cat.subcategories.all():
            print(f"  Subcategory: {sub.subcategory_name}, Products: {sub.products.count()}")
            for product in sub.products.all():
                print(f"    Product: {product.product_name}, Image Count: {product.product_images.count()}")

    products = Product.objects.prefetch_related('product_images', 'color_variant', 'size_variant').all()
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, "products/shop.html", context)
