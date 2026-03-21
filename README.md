# LogiCart Enhanced v5

Fully redesigned Django e-commerce platform — premium UI, 30 products, admin + shop panels.

## Quick Setup

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata shop/fixtures/products.json
python manage.py createsuperuser
python manage.py runserver
```

Visit: http://127.0.0.1:8000/shop/ | Admin: http://127.0.0.1:8000/dashboard/

## What's New
- 30 products across 7 categories (Electronics, Fashion, Beauty, Home, Sports, Books, Toys)
- Full shop UI: base.html, index, search, product detail, checkout, tracker, wishlist, contact, about
- CSS: Syne + DM Sans, #FF4D00 accent, card layouts, cart drawer, toast notifications
- JS: localStorage cart, wishlist toggle, coupon AJAX, newsletter
- Admin: restyled sidebar, stat cards, tables, add-product form
- "Made with love in India" footer removed — clean copyright footer

## Coupon Codes
Add in Django Admin: LOGI30 (30% off), FLAT100 (flat Rs.100), NEWUSER (20% off)
