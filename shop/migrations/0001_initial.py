from django.db import migrations, models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100)),
                ('category', models.CharField(db_index=True, default='', max_length=50)),
                ('subcategory', models.CharField(blank=True, default='', max_length=50)),
                ('price', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('original_price', models.PositiveIntegerField(default=0, help_text='Strike-through price before discount')),
                ('stock', models.PositiveIntegerField(default=0)),
                ('desc', models.TextField(blank=True, max_length=1000)),
                ('pub_date', models.DateField()),
                ('image', models.ImageField(default='', upload_to='shop/images')),
                ('is_featured', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-pub_date'],
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('msg_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(
                    blank=True, max_length=15,
                    validators=[django.core.validators.RegexValidator(r'^\+?[\d\s\-]{7,15}$', 'Enter a valid phone number.')]
                )),
                ('desc', models.TextField(max_length=2000)),
                ('is_read', models.BooleanField(default=False)),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Contact Message',
                'ordering': ['-submitted_at'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(db_index=True, max_length=20, unique=True)),
                ('discount_type', models.CharField(choices=[('percent', 'Percentage'), ('flat', 'Flat Amount')], default='percent', max_length=10)),
                ('discount_value', models.PositiveIntegerField(default=0)),
                ('min_order_amount', models.PositiveIntegerField(default=0)),
                ('max_uses', models.PositiveIntegerField(default=100)),
                ('used_count', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
            ],
            options={
                'ordering': ['-valid_to'],
            },
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('items_json', models.TextField(max_length=10000)),
                ('amount', models.PositiveIntegerField(default=0)),
                ('discount_amount', models.PositiveIntegerField(default=0)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='shop.coupon')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.CharField(max_length=300)),
                ('city', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=100)),
                ('zip_code', models.CharField(max_length=10)),
                ('phone', models.CharField(
                    max_length=15,
                    validators=[django.core.validators.RegexValidator(r'^\+?[\d\s\-]{7,15}$', 'Enter a valid phone number.')]
                )),
                ('status', models.CharField(
                    choices=[
                        ('placed', 'Order Placed'), ('processing', 'Processing'),
                        ('shipped', 'Shipped'), ('out_for_delivery', 'Out for Delivery'),
                        ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('refunded', 'Refunded'),
                    ],
                    default='placed', max_length=20
                )),
                ('payment_id', models.CharField(blank=True, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderUpdate',
            fields=[
                ('update_id', models.AutoField(primary_key=True, serialize=False)),
                ('order', models.ForeignKey(blank=True, db_column='order_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='shop.orders')),
                ('update_desc', models.TextField(max_length=5000)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Order Update',
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='shop.product')),
                ('name', models.CharField(max_length=80)),
                ('email', models.EmailField()),
                ('rating', models.PositiveSmallIntegerField(
                    validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)]
                )),
                ('comment', models.TextField(max_length=1000)),
                ('is_approved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(db_index=True, max_length=40)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlisted_by', to='shop.product')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-added_at'],
                'unique_together': {('session_key', 'product')},
            },
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(unique=True)),
                ('subscribed_at', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-subscribed_at'],
            },
        ),
        migrations.CreateModel(
            name='ReturnRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='return_requests', to='shop.orders')),
                ('reason', models.CharField(
                    choices=[
                        ('defective', 'Defective / Damaged'), ('wrong_item', 'Wrong Item Received'),
                        ('not_as_described', 'Not as Described'), ('changed_mind', 'Changed Mind'), ('other', 'Other'),
                    ],
                    max_length=30
                )),
                ('description', models.TextField(max_length=1000)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending Review'), ('approved', 'Approved'),
                        ('rejected', 'Rejected'), ('completed', 'Completed'),
                    ],
                    default='pending', max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('admin_note', models.TextField(blank=True, max_length=500)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
