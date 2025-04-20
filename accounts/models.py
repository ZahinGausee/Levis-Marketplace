
from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils.html import format_html
from django.utils.timezone import localtime

import uuid
from base.emails import send_account_activation_email
from products.models import Product, ColorVariant, SizeVariant, Coupon

# Create your models here.
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_image = models.ImageField(upload_to="profile", default="profiles/default.jpg")
    is_email_verified = models.BooleanField(default=False)
    email_token = models.CharField(max_length=100 , null=True , blank=True)
    address = models.CharField(max_length=255, null=True , blank=True)
    city = models.CharField(max_length=100, null=True , blank=True)
    state = models.CharField(max_length=100, null=True , blank=True)
    country = models.CharField(max_length=100, null=True , blank=True)
    phone = models.CharField(max_length=10, null=True , blank=True)
    zip_code = models.CharField(max_length=10, null=True , blank=True)

    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid = False, cart__user = self.user).count()
    
    def total_orders(self):
        """Returns the total number of orders placed by the user"""
        return self.user.orders.count()  # Assuming Order model has a ForeignKey to User

    def total_spent(self):
        """Returns the total amount spent by the user"""
        total_amount = sum(order.total_price for order in self.user.orders.all())  # Assuming Order model has a total_price field
        return f"₹{total_amount:.2f}"

    def display_profile_info(self):
        """Returns an HTML formatted table for profile overview"""
        return format_html(
            """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th style="padding: 5px;">User</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Email Verified</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Phone</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Address</th><td style="padding: 5px;">{}, {}, {}, {}</td></tr>
                <tr><th style="padding: 5px;">Zip Code</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Total Orders</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Total Spent</th><td style="padding: 5px;">{}</td></tr>
            </table>
            """,
            self.user.username,
            "✅ Yes" if self.is_email_verified else "❌ No",
            self.phone if self.phone else "Not Provided",
            self.address if self.address else "N/A",
            self.city if self.city else "N/A",
            self.state if self.state else "N/A",
            self.country if self.country else "N/A",
            self.zip_code if self.zip_code else "N/A",
            self.total_orders(),
            self.total_spent()
        )

    display_profile_info.short_description = "Profile Overview"
    

@receiver(post_save , sender = User)
def  send_email_token(sender , instance , created , **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user = instance , email_token = email_token)
            email = instance.email
            send_account_activation_email(email , email_token)

    except Exception as e:
         print(f"❌ Error in post_save signal: {e}")


class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        print(cart_items)
        price = []
        for cart_item in cart_items:
            price.append(cart_item.get_product_price())  
        
        if self.coupon:
            if sum(price) > self.coupon.minimum_amount:
                return sum(price) - self.coupon.discount_price
        
        return sum(price)
    
    
    def display_cart_info(self):
        """Returns an HTML formatted table for cart overview"""
        return format_html(
            """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th style="padding: 5px;">User</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Total Price</th><td style="padding: 5px;">₹{}</td></tr>
                <tr><th style="padding: 5px;">Coupon</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Paid</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Razorpay Order ID</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Razorpay Payment ID</th><td style="padding: 5px;">{}</td></tr>
            </table>
            """,
            self.user.username,
            self.get_cart_total(),
            self.coupon.coupon_code if self.coupon else "No Coupon",
            "✅ Yes" if self.is_paid else "❌ No",
            self.razor_pay_order_id if self.razor_pay_order_id else "N/A",
            self.razor_pay_payment_id if self.razor_pay_payment_id else "N/A"
        )
    display_cart_info.short_description = "Cart Overview"

    
    
class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="cart_product" )
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True )
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True )
    quantity = models.PositiveIntegerField(default=1)

    def get_product_price(self):
        price = [self.product.price]    

        if self.color_variant:
            color_variant_price = self.color_variant.price
            price.append(color_variant_price)
        if self.size_variant:
            size_variant_price = self.size_variant.price
            price.append(size_variant_price)

        return sum(price) * self.quantity
    
    def display_cart_item_info(self):
        """Returns an HTML table for cart item details."""
        return format_html(
            """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th style="padding: 5px;">Product</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Color</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Size</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Quantity</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Total Price</th><td style="padding: 5px;">₹{}</td></tr>
            </table>
            """,
            self.product.product_name if self.product else "Product Deleted",
            self.color_variant.color_name if self.color_variant else "No Color",
            self.size_variant.size_name if self.size_variant else "No Size",
            self.quantity,
            self.get_product_price()
        )

    display_cart_item_info.short_description = "Cart Item Overview"

class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=[("Pending", "Pending"), ("Shipped", "Shipped"), ("Delivered", "Delivered"), ("Cancelled", "Cancelled")], 
        default="Pending"
    )
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    invoice_file_name = models.CharField(max_length=255, null=True, blank=True)  


    def display_order_overview(self):
        """Returns an HTML formatted table for orders with Date & Time"""
        return format_html(
            """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th style="padding: 5px;">Order ID</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">User</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Total Price</th><td style="padding: 5px;">₹{:.2f}</td></tr>
                <tr><th style="padding: 5px;">Status</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Coupon</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Date & Time</th><td style="padding: 5px;">{}</td></tr>
            </table>
            """,
            self.uid,
            self.user.username,
            self.total_price,
            self.status,
            self.coupon if self.coupon else "No Coupon",
            localtime(self.created_at).strftime("%d-%m-%Y %I:%M %p")  # Formats date & time
        )

    display_order_overview.short_description = "Order Overview"
    

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    color_variant = models.ForeignKey(ColorVariant, on_delete=models.SET_NULL, null=True, blank=True)
    size_variant = models.ForeignKey(SizeVariant, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    

    def display_order_item(self):
        """Returns an HTML formatted table for order items"""
        return format_html(
            """
            <table border="1" style="border-collapse: collapse; width: 100%;">
                <tr><th style="padding: 5px;">Product</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Color</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Size</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Quantity</th><td style="padding: 5px;">{}</td></tr>
                <tr><th style="padding: 5px;">Price</th><td style="padding: 5px;">₹{:.2f}</td></tr>
                <tr><th style="padding: 5px;">Total Price</th><td style="padding: 5px; font-weight: bold;">₹{:.2f}</td></tr>
            </table>
            """,
            self.product.product_name if self.product else "Deleted Product",
            self.color_variant.color_name if self.color_variant else "No Color",
            self.size_variant.size_name if self.size_variant else "No Size",
            self.quantity,
            self.price,
            self.price * self.quantity
        )

    display_order_item.short_description = "Order Item Overview"