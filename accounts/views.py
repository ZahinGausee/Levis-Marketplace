from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
from products.models import Product, SizeVariant, ColorVariant, Coupon
from accounts.models import Profile, Cart, CartItems, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
import razorpay
from django.conf import settings
from base.helpers import save_pdf
from django.http import FileResponse
import os
# Create your views here.

def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        phone = request.POST.get('phone')
        zip_code = request.POST.get('zip_code')

        user_obj = User.objects.filter(username = email)
        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        # Create User
        user_obj = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=email
        )
        user_obj.set_password(password)
        user_obj.save()

        # Create Profile with Additional Fields
        profile = user_obj.profile
        profile.address=address
        profile.city=city
        profile.state=state
        profile.country=country
        profile.phone=phone
        profile.zip_code=zip_code
        profile.save()
        

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')


def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')
    

def user_logout(request):
    """Handles user logout and redirects to homepage."""
    logout(request)
    return redirect("/")


def cart(request):
    try:
        # Optimize query to reduce database hits
        user_cart = Cart.objects.filter(is_paid=False, user=request.user).select_related("user").prefetch_related("cart_items").first()

        if not user_cart or not user_cart.cart_items.exists():
            raise ValueError("Your cart is empty. Add items before proceeding.")

        cart_items = user_cart.cart_items.select_related("product").prefetch_related("product__product_images")

        # Handle coupon logic in POST request
        if request.method == 'POST':        
            return handle_coupon_application(request, user_cart)

        # Create Razorpay order
        client = razorpay.Client(auth=(settings.PUBLIC_RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount = user_cart.get_cart_total() * 100  # Convert to paisa
        try:
            payment = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})
            user_cart.razor_pay_order_id = payment['id']
            user_cart.save()
        except razorpay.errors.RazorpayError as e:
            messages.error(request, f"Payment error: {str(e)}")
            return render(request, "accounts/cart.html", {"cart": user_cart, "cart_items": cart_items, "payment": None})

        context = {
            "cart": user_cart,
            "cart_items": cart_items,
            "payment": payment
        }
        return render(request, "accounts/cart.html", context)

    except ValueError as e:
        messages.warning(request, str(e))
        return render(request, "accounts/cart.html", {"cart": None, "cart_items": [], "payment": None})

    except Exception as e:
        messages.error(request, f"Something went wrong: {e}")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def handle_coupon_application(request, user_cart):
    """Handles coupon validation and application."""
    coupon = request.POST.get('coupon')
    coupon_obj = Coupon.objects.filter(coupon_code__icontains=coupon).first()

    if not coupon_obj:
        messages.warning(request, 'Invalid Coupon Code')
    elif user_cart.coupon:
        messages.warning(request, 'Coupon Already Applied')
    elif user_cart.get_cart_total() < coupon_obj.minimum_amount:
        messages.warning(request, f"Minimum order amount should be ₹{coupon_obj.minimum_amount} to apply this coupon.")
    elif coupon_obj.is_expired:
        messages.warning(request, 'This coupon is expired.')
    else:
        user_cart.coupon = coupon_obj
        user_cart.save()
        messages.success(request, 'Coupon successfully applied!')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def remove_cart(request, cart_item_uid):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, cart_id):
    cart = Cart.objects.get(uid = cart_id)
    cart.coupon = None
    cart.save()
    messages.success(request, 'Coupon Removed')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def add_to_cart(request, uid):
    variant = request.GET.get('variant')
    color = request.GET.get('color')
    quantity = int(request.GET.get('quantity', 1))  # Get quantity from request
    product = Product.objects.get(uid=uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)

    if not user:
        messages.warning(request, 'Please sign in  first to add the cart.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    # Check if the item already exists in the cart
    cart_item = CartItems.objects.filter(
        cart=cart, product=product, size_variant__size_name=variant, color_variant__color_name=color
    ).first()

    if cart_item:
        cart_item.quantity += quantity  # Update quantity
        cart_item.save()
    else:
        # Create a new cart item
        cart_item = CartItems.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        if variant:
            size_variant = SizeVariant.objects.filter(size_name=variant).first()
            if size_variant:
                cart_item.size_variant = size_variant

        if color:
            color_variant = ColorVariant.objects.filter(color_name=color).first()
            if color_variant:
                cart_item.color_variant = color_variant

        cart_item.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def success(request):
    order_id = request.GET.get('razorpay_order_id')
    payment_id = request.GET.get('razorpay_payment_id')
    payment_signature = request.GET.get('razorpay_signature')

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.PUBLIC_RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        # Verify Razorpay payment signature
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': payment_signature
        }
        client.utility.verify_payment_signature(params_dict)
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"error": "Payment verification failed"}, status=400)

    cart = Cart.objects.filter(razor_pay_order_id=order_id).first()
    if not cart:
        return HttpResponse("Cart not found for the given Razorpay order ID.", status=404)

    cart.razor_pay_payment_id = payment_id
    cart.razor_pay_payment_signature = payment_signature
    cart.is_paid = True
    cart.save()

    user = cart.user
    cart_items = cart.cart_items.all()
    if not cart_items.exists():
        return JsonResponse({"error": "Cart is empty"}, status=400)

    total_price = cart.get_cart_total()

    with transaction.atomic():
        # Check stock availability
        for item in cart_items:
            if item.product.stock_quantity < item.quantity:
                return JsonResponse({
                    "error": f"Insufficient stock for {item.product.product_name}. Only {item.product.stock_quantity} left."
                }, status=400)
            
        # Create order
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            status="Pending",
            razor_pay_order_id=order_id,
            razor_pay_payment_id=payment_id,
            razor_pay_payment_signature=payment_signature,
            coupon=cart.coupon
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                color_variant=item.color_variant,
                size_variant=item.size_variant,
                quantity=item.quantity,
                price=item.product.price
            )
            print(item.product.stock_quantity, item.quantity)
            item.product.stock_quantity -= item.quantity
            item.product.save()

        cart_items.delete()
        cart.delete()

    # Generate PDF invoice
    for item in order.order_items.all():
        item.total_price = item.price * item.quantity
    invoice_data = {
        "order": order,
        'total_price': total_price
    }
    file_name, success = save_pdf(invoice_data)

    if not success:
        return JsonResponse({"error": "Failed to generate invoice PDF"}, status=500)

    file_path = os.path.join(settings.BASE_DIR, "public", "static", file_name)
    print(file_path)
    order.invoice_file_name = file_name
    order.save()
    # Serve the PDF file as a response
    return FileResponse(open(file_path, "rb"), content_type="application/pdf")


def user_details(request):
    user = request.user  # Fetch logged-in user
    profile = Profile.objects.get(user=user)  # Fetch user profile

    orders = Order.objects.filter(user=user).order_by('-created_at')[:5]  # Fetch latest 5

    context = {
        'user': user,
        'profile': profile,
        'orders': orders,
    }

    return render(request, 'accounts/user_details.html', context)

def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Get orders of the logged-in user


    context = {
        'orders': orders,
    }

    return render(request, 'accounts/user_orders.html', context)

# @login_required
# def create_order(request):
#     user = request.user

#     # Retrieve cart for the user
#     cart = get_object_or_404(Cart, user=user, is_paid=False)
#     cart_items = cart.cart_items.all()  

#     if not cart_items.exists():
#         return JsonResponse({"error": "Cart is empty"}, status=400)

#     total_price = cart.get_cart_total()

#     with transaction.atomic():  # Ensures atomicity (all or nothing)
#         # Create order
#         order = Order.objects.create(
#             user=user,
#             total_price=total_price,
#             status="Pending",  # Initial status
#             razor_pay_order_id=cart.razor_pay_order_id,
#             razor_pay_payment_id=cart.razor_pay_payment_id,
#             razor_pay_payment_signature=cart.razor_pay_payment_signature,
#         )

#         # Create OrderItems from CartItems
#         for item in cart_items:
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 color_variant=item.color_variant,
#                 size_variant=item.size_variant,
#                 quantity=item.quantity,
#                 price=item.product.price
#             )

#         # Clear the cart
#         cart_items.delete()
#         cart.delete()

#     return JsonResponse({"message": "Order placed successfully", "order_id": order.id})
