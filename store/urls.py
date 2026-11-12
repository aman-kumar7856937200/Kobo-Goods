
from django.urls import path
from . import views

urlpatterns = [

    # ======================================
    # HOME
    # ======================================

    path("", views.home, name="home"),
    path("catalogue/", views.catalogue_view, name="catalogue"),

    # ======================================
    # AUTHENTICATION
    # ======================================

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    # ======================================
    # PRODUCTS AND REVIEWS
    # ======================================

    path(
        "products/<int:product_id>/",
        views.product_detail_view,
        name="product_detail"
    ),

    path(
        "products/<int:product_id>/review/",
        views.submit_product_review_view,
        name="submit_product_review"
    ),

    path(
        "reviews/<int:review_id>/delete/",
        views.delete_product_review_view,
        name="delete_product_review"
    ),

    # ======================================
    # WISHLIST
    # ======================================

    path(
        "wishlist/",
        views.wishlist_view,
        name="wishlist"
    ),

    path(
        "wishlist/add/<int:product_id>/",
        views.add_to_wishlist,
        name="add_to_wishlist"
    ),

    path(
        "wishlist/remove/<int:item_id>/",
        views.remove_from_wishlist,
        name="remove_from_wishlist"
    ),

    path(
        "wishlist/move/<int:item_id>/",
        views.move_to_cart,
        name="move_to_cart"
    ),


    path(
        "wishlist/toggle/<int:product_id>/", 
        views.toggle_wishlist, 
        name="toggle_wishlist"
    ),


    # ======================================
    # SHOPPING CART
    # ======================================

    path("cart/", views.cart_view, name="cart"),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/update/<int:item_id>/",
        views.update_cart,
        name="update_cart"
    ),

    path(
        "cart/remove/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # ======================================
    # CHECKOUT AND PAYMENT
    # ======================================

    path("checkout/", views.checkout_view, name="checkout"),

    path(
        "demo-payment/<uuid:order_number>/",
        views.demo_payment_view,
        name="demo_payment"
    ),

    path(
        "order-confirmation/<uuid:order_number>/",
        views.order_confirmation_view,
        name="order_confirmation"
    ),

    # ======================================
    # ORDER HISTORY
    # ======================================

    path("my-orders/", views.my_orders_view, name="my_orders"),

    path(
        "my-orders/<uuid:order_number>/",
        views.order_detail_view,
        name="order_detail"
    ),

    path(
        "my-orders/<uuid:order_number>/cancel/",
        views.cancel_order_view,
        name="cancel_order"
    ),

]
