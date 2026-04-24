import uuid
import re
from datetime import timedelta

from urllib.parse import quote

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.views.decorators.http import require_POST

from .forms import CheckoutForm, PaymentDetailsForm
from .models import (
    User, Product, Category, Blog, Gallery,
    Cart, CartItem, Wishlist, Order, OrderItem, Enquiry, HeroImage
)


# ─── HOME ───────────────────────────────────────────────────────────
def home(request):
    hero = HeroImage.objects.filter(is_active=True).first()
    featured_products = Product.objects.all()[:8]
    categories = Category.objects.all()
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_obj = Wishlist.objects.filter(user=request.user).first()
        if wishlist_obj:
            wishlist_products = list(wishlist_obj.products.all())
    context = {
        'hero_image': hero.image if hero else None,
        'featured_products': featured_products,
        'categories': categories,
        'wishlist_products': wishlist_products,
    }
    return render(request, 'home.html', context)


# ─── BLOGS ──────────────────────────────────────────────────────────
def blogs(request):
    all_blogs = Blog.objects.order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': all_blogs})


# ─── GALLERY ────────────────────────────────────────────────────────
def gallery(request):
    images = Gallery.objects.order_by('-created_at')
    return render(request, 'gallery.html', {'images': images})


# ─── CATEGORIES ─────────────────────────────────────────────────────
def categories(request):
    all_categories = Category.objects.all()
    products       = Product.objects.select_related('category').all().order_by('id')

    # Static category cards (1–9) map to the first nine products by id so
    # “Shop now” / “Add” can hit real cart rows without changing the template layout.
    ordered = list(Product.objects.order_by('id')[:9])
    shop_product_ids = [None] * 9
    for i, p in enumerate(ordered):
        shop_product_ids[i] = p.pk

    shop_now_hrefs = []
    login_shop_hrefs = []
    add_hrefs = []
    login_add_hrefs = []
    for i in range(9):
        pid = shop_product_ids[i]
        if pid is None:
            shop_now_hrefs.append(None)
            login_shop_hrefs.append(None)
            add_hrefs.append(None)
            login_add_hrefs.append(None)
            continue
        add_to_cart_path = reverse('add_to_cart', kwargs={'product_id': pid})
        to_cart = f'{add_to_cart_path}?next={reverse("cart")}'
        to_categories = f'{add_to_cart_path}?next={reverse("categories")}'
        shop_now_hrefs.append(to_cart)
        login_shop_hrefs.append(f'{reverse("login")}?next={quote(to_cart, safe="")}')
        add_hrefs.append(to_categories)
        login_add_hrefs.append(f'{reverse("login")}?next={quote(to_categories, safe="")}')

    # wishlist products for the current user (to pre-fill liked hearts)
    wishlist_products = []
    if request.user.is_authenticated:
        wishlist_obj = Wishlist.objects.filter(user=request.user).first()
        if wishlist_obj:
            wishlist_products = list(wishlist_obj.products.all())

    return render(request, 'categories.html', {
        'categories':        all_categories,
        'products':          products,
        'wishlist_products': wishlist_products,
        'shop_now_hrefs':    shop_now_hrefs,
        'login_shop_hrefs':  login_shop_hrefs,
        'add_hrefs':         add_hrefs,
        'login_add_hrefs':   login_add_hrefs,
    })


# ─── SHOP ───────────────────────────────────────────────────────────
def shop(request):
    products = Product.objects.all()
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category__slug=category_filter)
    all_categories = Category.objects.all()
    return render(request, 'shop.html', {
        'products': products,
        'categories': all_categories,
        'active_category': category_filter,
    })


# ─── ABOUT ──────────────────────────────────────────────────────────
def about(request):
    return render(request, 'about.html')


# ─── CONTACT ────────────────────────────────────────────────────────
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        Enquiry.objects.create(name=name, email=email, phone=phone, message=message)
        messages.success(request, 'Your message has been sent!')
        return redirect('contact')
    return render(request, 'contact.html')


# ─── ENQUIRY ────────────────────────────────────────────────────────
def enquiry(request):
    products = Product.objects.all()
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        name = f"{first_name} {last_name}".strip()
        
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        raw_msg = request.POST.get('message', '')
        
        # Prepend subject securely inside message block
        full_message = f"[{subject}]\n{raw_msg}" if subject else raw_msg
        
        Enquiry.objects.create(name=name, email=email, phone=phone, message=full_message)
        
        messages.success(request, 'Enquiry submitted! We will contact you soon.')
        return redirect('enquiry')
    return render(request, 'enquiry.html', {'products': products})


# ─── AUTH ────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Login Successful')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Logout Successful')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm_password', '')
        
        # Validations
        if ' ' in username:
            messages.error(request, 'Username should follow proper format (no spaces).')
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messages.error(request, 'Email should be in valid format (e.g., name@gmail.com).')
        elif len(password) < 8:
            messages.error(request, 'Password is too short. It must be at least 8 characters.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists, please use a different email.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Registration and Login Successful')
            return redirect('home')
    return render(request, 'register.html')


# ─── PROFILE ─────────────────────────────────────────────────────────
@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.gender = request.POST.get('gender', user.gender)
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'profile.html', {'user': request.user})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully.')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'password_change.html', {'form': form})


# ─── ORDERS ──────────────────────────────────────────────────────────
@login_required
def orders(request):
    user_orders = (
        Order.objects.filter(user=request.user)
        .order_by('-created_at')
        .prefetch_related('items__product')
    )
    return render(request, 'orders.html', {'orders': user_orders})


# ─── NOTIFICATIONS ───────────────────────────────────────────────────
@login_required
def notifications(request):
    return render(request, 'notifications.html')


# ─── CART ────────────────────────────────────────────────────────────
@login_required
def cart(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    cart_obj = Cart.objects.prefetch_related('items__product__category').get(pk=cart_obj.pk)
    return render(request, 'cart.html', {'cart': cart_obj})

@login_required
def checkout(request):
    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            request.session['checkout_details'] = form.cleaned_data
            return redirect('payment')
    else:
        initial = request.session.get('checkout_details') or {}
        form = CheckoutForm(initial=initial)

    cart_obj = Cart.objects.prefetch_related('items__product__category').get(pk=cart_obj.pk)
    return render(request, 'checkout.html', {'cart': cart_obj, 'form': form})


@login_required
def payment(request):
    if not request.session.get('checkout_details'):
        messages.warning(request, 'Please complete billing details before payment.')
        return redirect('checkout')

    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        messages.info(request, 'Your cart is empty.')
        return redirect('cart')

    cart_obj = Cart.objects.prefetch_related('items__product__category').get(pk=cart_obj.pk)
    return render(request, 'payment.html', {
        'cart': cart_obj,
        'payment_form': PaymentDetailsForm(),
        'selected_payment': 'Google Pay',
    })


@login_required
def complete_order(request):
    if request.method != 'POST':
        return redirect('payment')
    if not request.session.get('checkout_details'):
        messages.warning(request, 'Please complete billing details before payment.')
        return redirect('checkout')

    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    if not cart_obj.items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    raw_pm = request.POST.get('payment_method', 'Google Pay').strip()
    if raw_pm not in ('UPI', 'Google Pay', 'PhonePe'):
        raw_pm = 'Google Pay'

    pay_form = PaymentDetailsForm(request.POST, payment_method=raw_pm)
    if not pay_form.is_valid():
        return render(
            request,
            'payment.html',
            {
                'cart': cart_obj,
                'payment_form': pay_form,
                'selected_payment': raw_pm,
            },
        )

    transaction_ref = uuid.uuid4().hex[:12].upper()

    order = Order.objects.create(
        user=request.user,
        total_amount=cart_obj.grand_total,
        status='confirmed',
        payment_method=raw_pm,
        transaction_ref=transaction_ref,
    )
    for item in cart_obj.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
    cart_obj.items.all().delete()
    request.session.pop('checkout_details', None)
    messages.success(request, 'Payment Successful! Your order has been placed.')
    return redirect('order_success', order_id=order.pk)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product__category'),
        pk=order_id,
        user=request.user,
    )
    delivery_date = (order.created_at.date() + timedelta(days=7)).strftime('%d %B %Y')
    return render(request, 'order_success.html', {
        'order': order,
        'delivery_date': delivery_date,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    return render(request, 'product_detail.html', {'product': product})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.stock < 1:
        messages.error(request, 'This product is out of stock.')
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts=settings.ALLOWED_HOSTS,
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('cart')

    cart_obj, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart_obj,
        product=product,
        defaults={'quantity': 1},
    )
    if created:
        messages.success(request, f'{product.name} added to your cart.')
    elif item.quantity >= product.stock:
        messages.warning(request, 'No more stock available for this product.')
    else:
        item.quantity += 1
        item.save()
        messages.success(request, f'Updated quantity for {product.name}.')

    next_url = request.GET.get('next')
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts=settings.ALLOWED_HOSTS,
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect('cart')


@login_required
def decrease_cart_item(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('cart')


@login_required
@require_POST
def clear_cart(request):
    cart_obj = Cart.objects.filter(user=request.user).first()
    if cart_obj:
        cart_obj.items.all().delete()
        messages.info(request, 'Your cart has been cleared.')
    return redirect('cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart')


# ─── WISHLIST ────────────────────────────────────────────────────────
@login_required
def wishlist(request):
    wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist.html', {'wishlist': wishlist_obj})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    wishlist_obj, _ = Wishlist.objects.get_or_create(user=request.user)
    if product in wishlist_obj.products.all():
        wishlist_obj.products.remove(product)
        messages.info(request, f'{product.name} removed from wishlist.')
    else:
        wishlist_obj.products.add(product)
        messages.success(request, f'{product.name} added to wishlist.')
    return redirect('wishlist')
