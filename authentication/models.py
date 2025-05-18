# authentications/models.py
from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    category_id = models.IntegerField(blank=True, null=True)
    supplier_id = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'products'   # говорим Django, что модель связана с таблицей products
        managed = False         # Django не будет пытаться создавать/изменять таблицу

    def __str__(self):
        return self.name

class Pickup_point(models.Model):
    id = models.AutoField(primary_key=True)
    address = models.CharField(max_length=255, null = False)
    phone = models.CharField(null=True)

    class Meta:
        db_table = 'pickup_points'
        managed = False

    def __str__(self):
        return f"Пункт выдачи | Адрес: {self.address}"

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    amount = models.IntegerField()
    pickup_point = models.ForeignKey(Pickup_point, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'orders'
        managed = False

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    amount_item = models.DecimalField(max_digits=10, decimal_places = 2)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity


class Support(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    text_complaint = models.CharField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'supports'
        managed = False

    def __str__(self):
        return f"Заявление #{self.id} | Пользователь {self.user}"

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null = False)
    description = models.CharField(max_length=255, null = True)

    class Meta:
        db_table = 'categories'
        managed = False

    def __str__(self):
        return f"Категория: {self.name}"

class Supplier(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length=255, null = False)
    contact_info = models.CharField(max_length=255, null = True)
    address = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'suppliers'
        managed = False

    def __str__(self):
        return f"Продавец: {self.name}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        """Подсчет общей стоимости товаров в корзине"""
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        """Стоимость всех единиц данного товара"""
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"