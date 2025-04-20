from django.shortcuts import render
from products.models import Product, Category, SubCategory

# Create your views here.
def index(request):
    men_category = Category.objects.filter(category_name__iexact="men").first()
    
    if men_category:
        men_subcategories = SubCategory.objects.filter(category=men_category)
        men = Product.objects.filter(sub_category__in=men_subcategories).order_by('-created_at')[:8]
    else:
        men = Product.objects.none()  # Return an empty queryset if no "Men" category exists


    women_category = Category.objects.filter(category_name__iexact="women").first()
    
    if women_category:
        women_subcategories = SubCategory.objects.filter(category=women_category)
        women = Product.objects.filter(sub_category__in=women_subcategories).order_by('-created_at')[:8]
    else:
        women = Product.objects.none()

    context = {'women': women, 'men': men}
    return render(request, 'home/index.html', context)

def about_us(request):
    return render(request, 'home/about.html')

def contact_us(request):
    return render(request, 'home/contact.html')