"""
Run this ONCE after migrate + loaddata to link all product images.
  python add_images.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Ecom.settings')
django.setup()
from shop.models import Product

images = {
    1:  'sony-wh1000xm5.jpg',
    2:  'apple-ipad-air.jpg',
    3:  'samsung-qled-tv.jpg',
    4:  'mi-robot-vacuum.jpg',
    5:  'bose-qc45.jpg',
    6:  'dji-mini-4-pro.jpg',
    7:  'oneplus-13.jpg',
    8:  'logitech-mx-master.jpg',
    9:  'nike-air-max-270.jpg',
    10: 'levis-511-jeans.jpg',
    11: 'adidas-ultraboost.jpg',
    12: 'rayban-aviator.jpg',
    13: 'fossil-gen6-watch.jpg',
    14: 'zara-blazer.jpg',
    15: 'dyson-airwrap.jpg',
    16: 'ordinary-skincare.jpg',
    17: 'philips-trimmer.jpg',
    18: 'mac-studio-fix.jpg',
    19: 'instant-pot-duo.jpg',
    20: 'dyson-v15-vacuum.jpg',
    21: 'philips-airfryer.jpg',
    22: 'ikea-kallax.jpg',
    23: 'decathlon-mtb.jpg',
    24: 'yoga-mat.jpg',
    25: 'wilson-tennis-racket.jpg',
    26: 'atomic-habits.jpg',
    27: 'deep-work.jpg',
    28: 'zero-to-one.jpg',
    29: 'lego-bugatti.jpg',
    30: 'nintendo-switch-lite.jpg',
}

print("\n Linking product images...\n")
ok = 0
for pk, fn in images.items():
    try:
        p = Product.objects.get(pk=pk)
        p.image = f'shop/images/{fn}'
        p.save()
        print(f"  OK  [{pk:02d}] {p.product_name}")
        ok += 1
    except Product.DoesNotExist:
        print(f"  --  [{pk:02d}] Not found")

print(f"\n Done! {ok}/{len(images)} products updated.\n")
