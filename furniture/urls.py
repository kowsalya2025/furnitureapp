from django.urls import path
from . import views

urlpatterns = [

    # ── Core Pages ──────────────────────────────────────
    path('',                    views.home,             name='home'),
    path('blogs/',              views.blogs,            name='blogs'),
    path('gallery/',            views.gallery,          name='gallery'),
    path('categories/',         views.categories,       name='categories'),
    path('shop/',               views.shop,             name='shop'),
    path('about/',              views.about,            name='about'),
    path('contact/',            views.contact,          name='contact'),
    path('enquiry/',            views.enquiry,          name='enquiry'),

    # ── Auth ─────────────────────────────────────────────
    path('login/',              views.login_view,       name='login'),
    path('logout/',             views.logout_view,      name='logout'),
    path('register/',           views.register_view,    name='register'),
    path('signup/',             views.register_view,    name='signup'),

    # ── Account ──────────────────────────────────────────
    path('profile/',            views.profile,          name='profile'),
    path('password-change/',    views.password_change,  name='password_change'),
    path('orders/',             views.orders,           name='orders'),
    path('notifications/',      views.notifications,    name='notifications'),

    # ── Cart ─────────────────────────────────────────────
    path('cart/',                           views.cart,             name='cart'),
    path('checkout/',                       views.checkout,         name='checkout'),
    path('payment/',                        views.payment,          name='payment'),
    path('order/complete/',                 views.complete_order,   name='complete_order'),
    path('order-success/<int:order_id>/',   views.order_success,    name='order_success'),
    path('cart/add/<int:product_id>/',      views.add_to_cart,      name='add_to_cart'),
    path('cart/decrease/<int:item_id>/',    views.decrease_cart_item, name='decrease_cart_item'),
    path('cart/clear/',                     views.clear_cart,       name='clear_cart'),
    path('cart/remove/<int:item_id>/',      views.remove_from_cart, name='remove_from_cart'),

    # ── Wishlist ─────────────────────────────────────────
    path('wishlist/',                           views.wishlist,         name='wishlist'),
    path('wishlist/toggle/<int:product_id>/',   views.toggle_wishlist,  name='toggle_wishlist'),


    path('product/<int:id>/', views.product_detail, name='product_detail'),

]