
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone

from .models import (
    Product,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    ProductReview,
)


GUEST_CART_KEY = "guest_cart"


# ==========================================
# CART HELPERS
# ==========================================

def get_cart_count(request):

    if request.user.is_authenticated:
        return sum(
            item.quantity
            for item in CartItem.objects.filter(user=request.user)
        )

    guest_cart = request.session.get(GUEST_CART_KEY, {})

    return sum(int(quantity) for quantity in guest_cart.values())


def merge_guest_cart(request, user):

    guest_cart = request.session.get(GUEST_CART_KEY, {})

    for product_id, quantity in guest_cart.items():

        try:
            product = Product.objects.get(
                id=product_id
            )

            cart_item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={
                    "quantity": min(int(quantity), product.stock)
                }
            )

            if not created:
                cart_item.quantity = min(
                    cart_item.quantity + int(quantity),
                    product.stock
                )
                cart_item.save()

        except (Product.DoesNotExist, ValueError, TypeError):
            continue

    request.session[GUEST_CART_KEY] = {}
    request.session.modified = True


def get_user_cart_items(request):

    if request.user.is_authenticated:

        return CartItem.objects.filter(
            user=request.user
        ).select_related("product")

    guest_cart = request.session.get(GUEST_CART_KEY, {})

    cart_items = []

    for product_id, quantity in guest_cart.items():

        try:
            product = Product.objects.get(id=product_id)

            cart_items.append({
                "product": product,
                "quantity": int(quantity),
                "subtotal": product.price * int(quantity),
                "id": product.id,
            })

        except (Product.DoesNotExist, ValueError, TypeError):
            continue

    return cart_items


def calculate_cart_totals(cart_items):

    subtotal = Decimal("0.00")

    for item in cart_items:

        if isinstance(item, dict):
            subtotal += item["subtotal"]
        else:
            subtotal += item.product.price * item.quantity

    delivery_charge = Decimal("0.00") if subtotal >= 1000 else Decimal("50.00")

    total = subtotal + delivery_charge

    return {
        "subtotal": subtotal,
        "delivery_charge": delivery_charge,
        "total": total,
    }


def clear_user_cart(request):

    if request.user.is_authenticated:

        CartItem.objects.filter(
            user=request.user
        ).delete()

    request.session[GUEST_CART_KEY] = {}
    request.session.modified = True


def record_order_status(order, status, note=""):

    OrderStatusHistory.objects.create(
        order=order,
        status=status,
        note=note
    )


# ==========================================
# HOME PAGE
# ==========================================

def home(request):

    products = Product.objects.filter(
        is_featured=True
    )

    return render(request, "home.html", {
        "products": products,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# USER REGISTRATION
# ==========================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = UserCreationForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            merge_guest_cart(request, user)

            messages.success(
                request,
                "Your account has been created successfully!"
            )

            return redirect("home")

    else:
        form = UserCreationForm()

    return render(request, "accounts/register.html", {
        "form": form,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# USER LOGIN
# ==========================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            merge_guest_cart(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect("home")

    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {
        "form": form,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# USER LOGOUT
# ==========================================

@login_required(login_url="login")
@require_POST
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out successfully."
    )

    return redirect("home")


# ==========================================
# USER PROFILE
# ==========================================

@login_required(login_url="login")
def profile_view(request):

    return render(request, "accounts/profile.html", {
        "cart_count": get_cart_count(request),
    })


# ==========================================
# ADD TO CART
# ==========================================

@require_POST
def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:

        messages.error(
            request,
            "Sorry, this product is out of stock."
        )

        return redirect("home")

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    quantity = max(1, quantity)

    if request.user.is_authenticated:

        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            defaults={
                "quantity": min(quantity, product.stock)
            }
        )

        if not created:

            cart_item.quantity = min(
                cart_item.quantity + quantity,
                product.stock
            )

            cart_item.save()

    else:

        guest_cart = request.session.get(
            GUEST_CART_KEY,
            {}
        )

        product_id_string = str(product.id)

        current_quantity = int(
            guest_cart.get(product_id_string, 0)
        )

        guest_cart[product_id_string] = min(
            current_quantity + quantity,
            product.stock
        )

        request.session[GUEST_CART_KEY] = guest_cart
        request.session.modified = True

    messages.success(
        request,
        f"{product.name} added to your cart!"
    )

    return redirect(request.META.get("HTTP_REFERER", "home"))


# ==========================================
# CART PAGE
# ==========================================

def cart_view(request):

    cart_items = get_user_cart_items(request)

    totals = calculate_cart_totals(cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "subtotal": totals["subtotal"],
        "delivery_charge": totals["delivery_charge"],
        "total": totals["total"],
        "cart_count": get_cart_count(request),
    })


# ==========================================
# UPDATE CART
# ==========================================

@require_POST
def update_cart(request, item_id):

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        return redirect("remove_from_cart", item_id=item_id)

    if request.user.is_authenticated:

        cart_item = get_object_or_404(
            CartItem,
            id=item_id,
            user=request.user
        )

        cart_item.quantity = min(
            quantity,
            cart_item.product.stock
        )

        cart_item.save()

    else:

        guest_cart = request.session.get(
            GUEST_CART_KEY,
            {}
        )

        product_id = str(item_id)

        if product_id in guest_cart:

            try:
                product = Product.objects.get(id=item_id)

                guest_cart[product_id] = min(
                    quantity,
                    product.stock
                )

                request.session[GUEST_CART_KEY] = guest_cart
                request.session.modified = True

            except Product.DoesNotExist:
                pass

    messages.success(
        request,
        "Your cart has been updated."
    )

    return redirect("cart")


# ==========================================
# REMOVE FROM CART
# ==========================================

@require_POST
def remove_from_cart(request, item_id):

    if request.user.is_authenticated:

        CartItem.objects.filter(
            id=item_id,
            user=request.user
        ).delete()

    else:

        guest_cart = request.session.get(
            GUEST_CART_KEY,
            {}
        )

        guest_cart.pop(str(item_id), None)

        request.session[GUEST_CART_KEY] = guest_cart
        request.session.modified = True

    messages.success(
        request,
        "Product removed from your cart."
    )

    return redirect("cart")


# ==========================================
# CHECKOUT
# ==========================================

@login_required(login_url="login")
def checkout_view(request):

    cart_items = list(
        CartItem.objects.filter(
            user=request.user
        ).select_related("product")
    )

    if not cart_items:

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect("cart")

    totals = calculate_cart_totals(cart_items)

    for item in cart_items:

        if item.quantity > item.product.stock:

            messages.error(
                request,
                f"Only {item.product.stock} units of {item.product.name} are available."
            )

            return redirect("cart")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        payment_method = request.POST.get(
            "payment_method",
            "Cash on Delivery"
        )

        if payment_method not in [
            "Demo Payment",
            "Cash on Delivery",
        ]:

            messages.error(
                request,
                "Please select a valid payment method."
            )

            return redirect("checkout")

        if not all([
            full_name,
            email,
            phone,
            address,
            city,
            state,
            postal_code,
        ]):

            messages.error(
                request,
                "Please fill in all delivery details."
            )

            return redirect("checkout")

        with transaction.atomic():

            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                subtotal=totals["subtotal"],
                delivery_charge=totals["delivery_charge"],
                total_amount=totals["total"],
                payment_method=payment_method,
                payment_status="Pending",
                status="Pending",
            )

            for item in cart_items:

                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                )

            record_order_status(
                order,
                "Pending",
                "Order placed successfully."
            )

            clear_user_cart(request)

        if payment_method == "Demo Payment":

            return redirect(
                "demo_payment",
                order_number=order.order_number
            )

        return redirect(
            "order_confirmation",
            order_number=order.order_number
        )

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "subtotal": totals["subtotal"],
        "delivery_charge": totals["delivery_charge"],
        "total": totals["total"],
        "cart_count": get_cart_count(request),
    })


# ==========================================
# COMPLETE ORDER
# ==========================================

@login_required(login_url="login")
def complete_order(request, order_number):

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    with transaction.atomic():

        order = Order.objects.select_for_update().get(
            id=order.id
        )

        if order.status != "Pending":

            messages.warning(
                request,
                "This order has already been processed."
            )

            return redirect(
                "order_confirmation",
                order_number=order.order_number
            )

        order_items = list(
            order.items.select_related("product")
        )

        for item in order_items:

            if item.product_id is None:
                continue

            product = Product.objects.select_for_update().get(
                id=item.product_id
            )

            if product.stock < item.quantity:

                messages.error(
                    request,
                    f"Insufficient stock for {product.name}."
                )

                return redirect("cart")

            product.stock -= item.quantity

            product.save(
                update_fields=["stock"]
            )

        order.status = "Confirmed"

        order.save(
            update_fields=["status", "updated_at"]
        )

        record_order_status(
            order,
            "Confirmed",
            "Order confirmed successfully."
        )

    return redirect(
        "order_confirmation",
        order_number=order.order_number
    )


# ==========================================
# DEMO PAYMENT
# ==========================================

@login_required(login_url="login")
def demo_payment_view(request, order_number):

    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user
    )

    if order.payment_status == "Successful":

        return redirect(
            "order_confirmation",
            order_number=order.order_number
        )

    if request.method == "POST":

        payment_result = request.POST.get(
            "payment_result",
            "success"
        )

        if payment_result == "success":

            order.payment_status = "Successful"

            order.save(
                update_fields=["payment_status", "updated_at"]
            )

            complete_order(
                request,
                order.order_number
            )

            return redirect(
                "order_confirmation",
                order_number=order.order_number
            )

        else:

            with transaction.atomic():

                order = Order.objects.select_for_update().get(
                    id=order.id
                )

                order.payment_status = "Failed"
                order.status = "Cancelled"

                order.save(
                    update_fields=[
                        "payment_status",
                        "status",
                        "updated_at",
                    ]
                )

                record_order_status(
                    order,
                    "Cancelled",
                    "Demo payment failed."
                )

            messages.error(
                request,
                "Payment failed. Your order has been cancelled."
            )

            return redirect(
                "order_confirmation",
                order_number=order.order_number
            )

    return render(request, "demo_payment.html", {
        "order": order,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# ORDER CONFIRMATION
# ==========================================

@login_required(login_url="login")
def order_confirmation_view(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "status_history"
        ),
        order_number=order_number,
        user=request.user
    )

    return render(request, "order_confirmation.html", {
        "order": order,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# MY ORDERS
# ==========================================

@login_required(login_url="login")
def my_orders_view(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items",
        "status_history"
    )

    return render(request, "my_orders.html", {
        "orders": orders,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# INDIVIDUAL ORDER DETAILS
# ==========================================

@login_required(login_url="login")
def order_detail_view(request, order_number):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "status_history"
        ),
        order_number=order_number,
        user=request.user
    )

    can_cancel = order.status in [
        "Pending",
        "Confirmed",
        "Processing",
    ]

    return render(request, "order_detail.html", {
        "order": order,
        "can_cancel": can_cancel,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# CUSTOMER ORDER CANCELLATION
# ==========================================

@login_required(login_url="login")
@require_POST
def cancel_order_view(request, order_number):

    cancellation_reason = request.POST.get(
        "cancellation_reason",
        ""
    ).strip()

    if not cancellation_reason:

        messages.error(
            request,
            "Please provide a reason for cancelling your order."
        )

        return redirect(
            "order_detail",
            order_number=order_number
        )

    if len(cancellation_reason) > 500:

        messages.error(
            request,
            "Cancellation reason cannot exceed 500 characters."
        )

        return redirect(
            "order_detail",
            order_number=order_number
        )

    with transaction.atomic():

        order = get_object_or_404(
            Order.objects.select_for_update(),
            order_number=order_number,
            user=request.user
        )

        if order.status == "Cancelled":

            messages.warning(
                request,
                "This order has already been cancelled."
            )

            return redirect(
                "order_detail",
                order_number=order.order_number
            )

        if order.status not in [
            "Pending",
            "Confirmed",
            "Processing",
        ]:

            messages.error(
                request,
                "This order can no longer be cancelled because it has been shipped or delivered."
            )

            return redirect(
                "order_detail",
                order_number=order.order_number
            )

        previous_status = order.status

        # Restore stock only if it was previously deducted.
        if previous_status in [
            "Confirmed",
            "Processing",
        ]:

            order_items = list(
                order.items.select_related("product")
            )

            for item in order_items:

                if item.product_id is None:
                    continue

                product = Product.objects.select_for_update().get(
                    id=item.product_id
                )

                product.stock += item.quantity

                product.save(
                    update_fields=["stock"]
                )

        # Handle payment status.
        if order.payment_status == "Successful":

            order.payment_status = "Refund Pending"

        elif order.payment_status == "Pending":

            # COD orders remain unpaid.
            # Pending demo payments remain unpaid too.
            pass

        order.status = "Cancelled"
        order.cancellation_reason = cancellation_reason
        order.cancelled_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "payment_status",
                "cancellation_reason",
                "cancelled_at",
                "updated_at",
            ]
        )

        record_order_status(
            order,
            "Cancelled",
            f"Customer cancellation: {cancellation_reason}"
        )

    messages.success(
        request,
        "Your order has been cancelled successfully."
    )

    return redirect(
        "order_detail",
        order_number=order_number
    )


# ==========================================
# PRODUCT DETAILS AND CUSTOMER REVIEWS
# ==========================================

def user_can_review_product(user, product):
    """
    A customer can review a product only if they have
    purchased it and the order has been marked Delivered.
    """

    if not user.is_authenticated:
        return False

    return OrderItem.objects.filter(
        order__user=user,
        order__status="Delivered",
        product=product,
    ).exists()


def update_product_rating(product):
    """
    Recalculate product average rating and review count
    whenever a review is created, updated, or deleted.
    """

    review_data = ProductReview.objects.filter(
        product=product
    ).aggregate(
        average_rating=Avg("rating"),
        total_reviews=Count("id"),
    )

    average_rating = review_data["average_rating"] or 0
    total_reviews = review_data["total_reviews"] or 0

    product.rating = round(average_rating, 1)
    product.review_count = total_reviews

    product.save(
        update_fields=["rating", "review_count"]
    )


def product_detail_view(request, product_id):

    product = get_object_or_404(
        Product.objects.prefetch_related("reviews__user"),
        id=product_id
    )

    reviews = product.reviews.select_related("user").all()

    existing_review = None
    can_review = False

    if request.user.is_authenticated:

        existing_review = reviews.filter(
            user=request.user
        ).first()

        can_review = user_can_review_product(
            request.user,
            product
        )

    return render(request, "product_detail.html", {
        "product": product,
        "reviews": reviews,
        "existing_review": existing_review,
        "can_review": can_review,
        "cart_count": get_cart_count(request),
    })


# ==========================================
# SUBMIT OR UPDATE PRODUCT REVIEW
# ==========================================

@login_required(login_url="login")
@require_POST
def submit_product_review_view(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if not user_can_review_product(request.user, product):

        messages.error(
            request,
            "You can review this product after its order has been delivered."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    rating_value = request.POST.get(
        "rating",
        ""
    ).strip()

    title = request.POST.get(
        "title",
        ""
    ).strip()

    comment = request.POST.get(
        "comment",
        ""
    ).strip()

    try:
        rating_value = int(rating_value)

    except (TypeError, ValueError):
        rating_value = 0

    if rating_value not in range(1, 6):

        messages.error(
            request,
            "Please select a rating from 1 to 5."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    if not title:

        messages.error(
            request,
            "Please enter a review title."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    if len(title) > 150:

        messages.error(
            request,
            "Review title cannot exceed 150 characters."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    if not comment:

        messages.error(
            request,
            "Please write your review."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    if len(comment) > 1000:

        messages.error(
            request,
            "Review cannot exceed 1000 characters."
        )

        return redirect(
            "product_detail",
            product_id=product.id
        )

    review, created = ProductReview.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            "rating": rating_value,
            "title": title,
            "comment": comment,
        }
    )

    update_product_rating(product)

    if created:

        messages.success(
            request,
            "Your review has been submitted."
        )

    else:

        messages.success(
            request,
            "Your review has been updated."
        )

    return redirect(
        "product_detail",
        product_id=product.id
    )


# ==========================================
# DELETE PRODUCT REVIEW
# ==========================================

@login_required(login_url="login")
@require_POST
def delete_product_review_view(request, review_id):

    review = get_object_or_404(
        ProductReview.objects.select_related("product"),
        id=review_id
    )

    if review.user_id != request.user.id:

        messages.error(
            request,
            "You cannot delete another customer's review."
        )

        return redirect(
            "product_detail",
            product_id=review.product_id
        )

    product = review.product

    review.delete()

    update_product_rating(product)

    messages.success(
        request,
        "Your review has been deleted."
    )

    return redirect(
        "product_detail",
        product_id=product.id
    )
