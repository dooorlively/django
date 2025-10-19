from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    caliber = models.CharField(max_length=50)
    ammo_type = models.CharField(max_length=50)
    designation = models.CharField(max_length=100)
    penetration = models.IntegerField()
    fragmentation = models.FloatField()
    price = models.FloatField()
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    availability_status = models.CharField(max_length=50, blank=True, null=True)
    restock_hours = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.designation

class Vest(models.Model):
    model = models.CharField(max_length=100)
    protection_level = models.CharField(max_length=50)
    weight = models.FloatField()
    price = models.FloatField()
    image = models.ImageField(upload_to='uploads/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    availability_status = models.CharField(max_length=50, blank=True, null=True)
    restock_hours = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.model

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('product', 'Product'),
        ('vest', 'Vest'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)
    vest = models.ForeignKey(Vest, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField(default=1)
    price_at_time = models.FloatField()
    item_type = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)

    def __str__(self):
        return f"{self.item_type}: {self.product or self.vest} x {self.quantity}"
