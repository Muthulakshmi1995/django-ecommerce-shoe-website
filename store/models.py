from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.CharField(max_length=180, blank=True, help_text="Static product image path, e.g. store/products/asset_01.jpg")
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=160)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    mrp = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image = models.CharField(max_length=180, help_text="Static product image path, e.g. store/products/asset_01.jpg")
    image_2 = models.CharField(max_length=180, blank=True)
    image_3 = models.CharField(max_length=180, blank=True)
    image_4 = models.CharField(max_length=180, blank=True)
    colours = models.CharField(max_length=120, default="Black,Tan,Red")
    sizes = models.CharField(max_length=100, default="41,42,43,44,45")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)
    reviews = models.PositiveIntegerField(default=5)
    stock = models.PositiveIntegerField(default=25)
    featured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def image_list(self):
        return [x for x in [self.image, self.image_2, self.image_3, self.image_4] if x]

    @property
    def size_list(self):
        return [s.strip() for s in self.sizes.split(",") if s.strip()]

    @property
    def colour_list(self):
        return [s.strip() for s in self.colours.split(",") if s.strip()]

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"), ("paid", "Paid"), ("failed", "Failed"),
        ("processing", "Processing"), ("shipped", "Shipped"), ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    address = models.TextField()
    city = models.CharField(max_length=80)
    postal_code = models.CharField(max_length=12)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    razorpay_order_id = models.CharField(max_length=120, blank=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=160)
    size = models.CharField(max_length=10)
    colour = models.CharField(max_length=40, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

class Enquiry(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=25, blank=True)
    subject = models.CharField(max_length=180, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject or 'Enquiry'}"
