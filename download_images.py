"""
LogiCart — Auto Image Downloader
=================================
Run this script ONCE on your PC from inside the project folder:

    python download_images.py

It will download real product images from Unsplash (free, no account needed)
and save them directly into:  media/shop/images/

Then run:  python add_images.py
"""

import os
import urllib.request
import time

SAVE_DIR = os.path.join(os.path.dirname(__file__), "media", "shop", "images")
os.makedirs(SAVE_DIR, exist_ok=True)

# Real Unsplash photo URLs — free, no API key needed
# Format: (filename, unsplash_photo_url)
IMAGES = [
    # Electronics
    ("sony-wh1000xm5.jpg",
     "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=85&fit=crop"),

    ("apple-ipad-air.jpg",
     "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=85&fit=crop"),

    ("samsung-qled-tv.jpg",
     "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&q=85&fit=crop"),

    ("mi-robot-vacuum.jpg",
     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=85&fit=crop"),

    ("bose-qc45.jpg",
     "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=85&fit=crop"),

    ("dji-mini-4-pro.jpg",
     "https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=600&q=85&fit=crop"),

    ("oneplus-13.jpg",
     "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=85&fit=crop"),

    ("logitech-mx-master.jpg",
     "https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&q=85&fit=crop"),

    # Fashion
    ("nike-air-max-270.jpg",
     "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=85&fit=crop"),

    ("levis-511-jeans.jpg",
     "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=85&fit=crop"),

    ("adidas-ultraboost.jpg",
     "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&q=85&fit=crop"),

    ("rayban-aviator.jpg",
     "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=85&fit=crop"),

    ("fossil-gen6-watch.jpg",
     "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=85&fit=crop"),

    ("zara-blazer.jpg",
     "https://images.unsplash.com/photo-1594938298603-c8148c4b4357?w=600&q=85&fit=crop"),

    # Beauty
    ("dyson-airwrap.jpg",
     "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=600&q=85&fit=crop"),

    ("ordinary-skincare.jpg",
     "https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600&q=85&fit=crop"),

    ("philips-trimmer.jpg",
     "https://images.unsplash.com/photo-1621607512214-68297480165e?w=600&q=85&fit=crop"),

    ("mac-studio-fix.jpg",
     "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&q=85&fit=crop"),

    # Home
    ("instant-pot-duo.jpg",
     "https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&q=85&fit=crop"),

    ("dyson-v15-vacuum.jpg",
     "https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600&q=85&fit=crop"),

    ("philips-airfryer.jpg",
     "https://images.unsplash.com/photo-1648079866318-07d074a9e8cc?w=600&q=85&fit=crop"),

    ("ikea-kallax.jpg",
     "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=85&fit=crop"),

    # Sports
    ("decathlon-mtb.jpg",
     "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&q=85&fit=crop"),

    ("yoga-mat.jpg",
     "https://images.unsplash.com/photo-1601925228008-8f4c7f49f7b8?w=600&q=85&fit=crop"),

    ("wilson-tennis-racket.jpg",
     "https://images.unsplash.com/photo-1617883861744-45b47a8c7e6c?w=600&q=85&fit=crop"),

    # Books
    ("atomic-habits.jpg",
     "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=85&fit=crop"),

    ("deep-work.jpg",
     "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600&q=85&fit=crop"),

    ("zero-to-one.jpg",
     "https://images.unsplash.com/photo-1589998059171-988d887df646?w=600&q=85&fit=crop"),

    # Toys
    ("lego-bugatti.jpg",
     "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=85&fit=crop"),

    ("nintendo-switch-lite.jpg",
     "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=85&fit=crop"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def download(filename, url):
    path = os.path.join(SAVE_DIR, filename)
    if os.path.exists(path) and os.path.getsize(path) > 5000:
        print(f"  SKIP  {filename}  (already exists)")
        return True
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    if len(data) < 5000:
        raise ValueError(f"File too small ({len(data)} bytes) — likely an error page")
    with open(path, "wb") as f:
        f.write(data)
    return True

print("\n" + "="*52)
print("  LogiCart — Downloading 30 Product Images")
print("="*52 + "\n")
print(f"  Saving to: {SAVE_DIR}\n")

ok = 0
fail = 0
failed_list = []

for i, (filename, url) in enumerate(IMAGES, 1):
    try:
        download(filename, url)
        size = os.path.getsize(os.path.join(SAVE_DIR, filename))
        print(f"  [{i:02d}/30]  OK  {filename}  ({size//1024}KB)")
        ok += 1
        time.sleep(0.3)  # be polite to the server
    except Exception as e:
        print(f"  [{i:02d}/30]  FAIL  {filename}")
        print(f"          Error: {e}")
        fail += 1
        failed_list.append(filename)

print(f"\n{'='*52}")
print(f"  Done!  {ok} downloaded   {fail} failed")
print(f"{'='*52}")

if failed_list:
    print(f"\n  Failed files (retry manually):")
    for f in failed_list:
        print(f"    - {f}")

if ok > 0:
    print(f"\n  Next step — run:")
    print(f"    python add_images.py")

print()
