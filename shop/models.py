from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.contrib.auth.models import User


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, default='', db_index=True)
    subcategory = models.CharField(max_length=50, default='', blank=True)
    price = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    original_price = models.PositiveIntegerField(default=0, help_text='Strike-through price before discount')
    stock = models.PositiveIntegerField(default=0)
    desc = models.TextField(max_length=1000, blank=True)
    pub_date = models.DateField()
    image = models.ImageField(upload_to='shop/images', default='')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f'{self.product_name} (Rs.{self.price})'

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return round((self.original_price - self.price) / self.original_price * 100)
        return 0

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def in_stock(self):
        return self.stock > 0


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(
        max_length=15, blank=True,
        validators=[RegexValidator(r'^\+?[\d\s\-]{7,15}$', 'Enter a valid phone number.')]
    )
    desc = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Contact Message'

    def __str__(self):
        return f'{self.name} <{self.email}>'


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [('percent', 'Percentage'), ('flat', 'Flat Amount')]
    code = models.CharField(max_length=20, unique=True, db_index=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, default='percent')
    discount_value = models.PositiveIntegerField(default=0)
    min_order_amount = models.PositiveIntegerField(default=0)
    max_uses = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField()
    valid_to = models.DateField()

    class Meta:
        ordering = ['-valid_to']

    def __str__(self):
        return f'{self.code} ({self.discount_value}{"%" if self.discount_type=="percent" else " Rs off"})'

    def is_valid(self, order_amount=0):
        from django.utils import timezone
        today = timezone.now().date()
        return (
            self.is_active
            and self.valid_from <= today <= self.valid_to
            and self.used_count < self.max_uses
            and order_amount >= self.min_order_amount
        )

    def apply(self, amount):
        if self.discount_type == 'percent':
            return max(0, amount - int(amount * self.discount_value / 100))
        return max(0, amount - self.discount_value)


class Orders(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Order Placed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    order_id = models.AutoField(primary_key=True)
    items_json = models.TextField(max_length=10000)
    amount = models.PositiveIntegerField(default=0)
    discount_amount = models.PositiveIntegerField(default=0)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL, related_name='orders')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?[\d\s\-]{7,15}$', 'Enter a valid phone number.')]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    payment_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order #{self.order_id} - {self.name} (Rs.{self.amount})'


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='updates', null=True, blank=True, db_column='order_id')
    update_desc = models.TextField(max_length=5000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Order Update'

    def __str__(self):
        return f'[Order #{self.order_id}] {self.update_desc[:50]}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.product.product_name} ({self.rating}★)'


class Wishlist(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session_key', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f'Wishlist: {self.product.product_name}'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class ReturnRequest(models.Model):
    REASON_CHOICES = [
        ('defective', 'Defective / Damaged'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='return_requests')
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_note = models.TextField(max_length=500, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Return #{self.pk} for Order #{self.order_id} ({self.status})'
