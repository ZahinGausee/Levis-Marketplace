from django.db import models
from base.models import BaseModel
from django.utils.text import slugify

# Create your models here.
class Category(BaseModel):
    category_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to="categories/")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.category_name

class SubCategory(BaseModel):
    subcategory_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    subcategory_image = models.ImageField(upload_to="categories/subcategories/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def save(self, *args, **kwargs):
        self.slug = slugify(self.subcategory_name)
        super(SubCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.subcategory_name
    
class ColorVariant(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.color_name

class SizeVariant(BaseModel):
    size_name = models.CharField(max_length=100, default="Default Size")
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.size_name

class Product(BaseModel):
    product_name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    price = models.IntegerField()
    RRP = models.IntegerField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField()
    product_description = models.TextField()
    color_variant = models.ManyToManyField(ColorVariant, blank=True ,related_name='color_variant')
    size_variant = models.ManyToManyField(SizeVariant, blank=True, related_name='size_variant')
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="products")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
    def get_product_price_by_size(self, size):
        return self.price + SizeVariant.objects.get(size_name=size).price

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.CASCADE, related_name="color_images", null=True, blank=True)
    image = models.ImageField(upload_to="product/")

    def __str__(self):
        if self.color_variant:
            return f"Image for {self.product.product_name} - {self.color_variant.color_name}"
        return f"Image for {self.product.product_name}"

class Coupon(BaseModel):
    coupon_code = models.CharField(max_length=10)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)

    def __str__(self):
        return self.coupon_code
    