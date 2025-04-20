from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Supplier)

class OrderItemInLine(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = [
    "id",
    "user",
    # "product_name",
    # "product_quantity",
    "amount",
    ]
    list_filter = ["pickup_point"]

    inlines = [OrderItemInLine]

admin.site.register(Order, OrderAdmin)