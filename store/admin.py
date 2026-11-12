
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import (
    Product,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
)


# ==========================================
# PRODUCT ADMIN
# ==========================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "original_price",
        "stock",
        "rating",
        "is_featured",
    )

    list_filter = (
        "category",
        "is_featured",
        "badge",
    )

    search_fields = ("name", "description")

    list_editable = ("price", "stock", "is_featured")

    readonly_fields = ("created_at",)


# ==========================================
# CART ITEM ADMIN
# ==========================================

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "product",
        "quantity",
        "added_at",
    )

    search_fields = (
        "user__username",
        "product__name",
    )

    list_filter = ("added_at",)

    readonly_fields = ("added_at",)


# ==========================================
# ORDER ITEM INLINE
# ==========================================

class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0
    can_delete = False

    fields = (
        "product_name",
        "product_price",
        "quantity",
        "subtotal_display",
    )

    readonly_fields = (
        "product_name",
        "product_price",
        "quantity",
        "subtotal_display",
    )

    def subtotal_display(self, obj):
        return obj.subtotal if obj else "-"

    subtotal_display.short_description = "Subtotal"

    def has_add_permission(self, request, obj=None):
        return False


# ==========================================
# ORDER STATUS HISTORY INLINE
# ==========================================

class OrderStatusHistoryInline(admin.TabularInline):

    model = OrderStatusHistory
    extra = 0
    can_delete = False

    fields = (
        "status",
        "note",
        "created_at",
    )

    readonly_fields = (
        "status",
        "note",
        "created_at",
    )

    def has_add_permission(self, request, obj=None):
        return False


# ==========================================
# ORDER ADMIN
# ==========================================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "order_number",
        "full_name",
        "user",
        "total_amount",
        "status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order_number",
        "full_name",
        "email",
        "phone",
        "user__username",
    )

    # Status is changed on the order detail page,
    # so that every change can be recorded.
    list_editable = ()

    readonly_fields = (
        "order_number",
        "user",
        "subtotal",
        "delivery_charge",
        "total_amount",
        "created_at",
        "updated_at",
        "cancelled_at",
    )

    fieldsets = (
        ("Order Information", {
            "fields": (
                "order_number",
                "user",
                "status",
                "created_at",
                "updated_at",
            )
        }),

        ("Customer Information", {
            "fields": (
                "full_name",
                "email",
                "phone",
            )
        }),

        ("Delivery Address", {
            "fields": (
                "address",
                "city",
                "state",
                "postal_code",
            )
        }),

        ("Payment Information", {
            "fields": (
                "payment_method",
                "payment_status",
            )
        }),

        ("Cancellation Information", {
            "fields": (
                "cancellation_reason",
                "cancelled_at",
            )
        }),

        ("Order Amount", {
            "fields": (
                "subtotal",
                "delivery_charge",
                "total_amount",
            )
        }),
    )

    inlines = [
        OrderItemInline,
        OrderStatusHistoryInline,
    ]

    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):

        old_status = None

        if change:
            old_order = Order.objects.get(pk=obj.pk)
            old_status = old_order.status

        # Do not allow admin to cancel an order directly.
        # Customer cancellation uses the stock-restoration workflow.
        if (
            change
            and old_status != "Cancelled"
            and obj.status == "Cancelled"
        ):
            raise ValidationError(
                "Use the customer cancellation workflow to cancel "
                "an order safely. This restores stock and records "
                "the cancellation reason."
            )

        super().save_model(request, obj, form, change)

        if change and old_status != obj.status:

            OrderStatusHistory.objects.create(
                order=obj,
                status=obj.status,
                note=f"Order status updated by admin ({request.user.username})."
            )

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================================
# ORDER STATUS HISTORY ADMIN
# ==========================================

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "status",
        "note",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order__order_number",
        "order__full_name",
        "note",
    )

    readonly_fields = (
        "order",
        "status",
        "note",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
